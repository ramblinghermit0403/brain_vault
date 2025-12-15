import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

# LangChain Imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory
from pydantic import BaseModel, Field
from langchain_core.tools import tool, StructuredTool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

# App Imports
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.chat import ChatMessage, ChatSession, MessageRole
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

# --- 1. Custom Memory History ---
class SQLChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, user_id: int):
        self.session_id = session_id
        self.user_id = user_id
        
    @property
    def messages(self) -> List[BaseMessage]:
        # Sync wrapper not ideal for async DB, but LangChain BaseChatMessageHistory is sync-ish.
        # We'll use a helper or run generic sync code if needed, 
        # BUT RunnableWithMessageHistory supports async methods if we implement `aget_messages`?
        # Actually standard practice in async FastAPI + LangChain is tricky.
        # We will use a hack: load messages effectively before calling agent, 
        # OR implementation aget_messages.
        raise NotImplementedError("Use aget_messages for async")

    async def aget_messages(self) -> List[BaseMessage]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == int(self.session_id))
                .order_by(ChatMessage.created_at.asc())
            )
            rows = result.scalars().all()
            
            messages = []
            for row in rows:
                if row.role == MessageRole.USER:
                    messages.append(HumanMessage(content=row.content))
                elif row.role == MessageRole.ASSISTANT:
                    messages.append(AIMessage(content=row.content))
                elif row.role == MessageRole.SYSTEM:
                    messages.append(SystemMessage(content=row.content))
            return messages

    async def add_message(self, message: BaseMessage) -> None:
        async with AsyncSessionLocal() as db:
            role = MessageRole.USER
            if isinstance(message, AIMessage):
                role = MessageRole.ASSISTANT
            elif isinstance(message, SystemMessage):
                role = MessageRole.SYSTEM
                
            db_msg = ChatMessage(
                session_id=int(self.session_id),
                role=role,
                content=message.content,
                created_at=datetime.utcnow()
            )
            db.add(db_msg)
            await db.commit()
            
    async def clear(self) -> None:
        pass

# --- 2. Tools ---

class SearchMemoryInput(BaseModel):
    query: str = Field(description="The query to search for in the brain vault.")

@tool("search_memory", args_schema=SearchMemoryInput)
def search_memory_tool(query: str):
    """Search for relevant memories, notes, and documents in the Brain Vault."""
    # This calls our vector store
    # Note: vector_store.query is synchronous or we wrap it?
    # vector_store.query is NOT async in the code I saw earlier (it calls pinecone directly).
    # But checking vector_store.py... 
    # `def query(self, query_texts: str, ...)` -> It is synchronous.
    
    results = vector_store.query(query, n_results=5)
    
    if not results["documents"] or not results["documents"][0]:
        return "No relevant memories found."
        
    # Format
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    ids = results["ids"][0]
    
    formatted = []
    for i, doc in enumerate(docs):
        meta = metas[i] if i < len(metas) else {}
        # Prefer memory_id from metadata (DB ID), fallback to document_id, then vector ID
        doc_id = meta.get("memory_id")
        if not doc_id:
             doc_id = meta.get("document_id")
        
        if not doc_id:
             doc_id = ids[i] if i < len(ids) else "unknown"
             
        title = meta.get("title", "Untitled")
        formatted.append(f"Source: {title} [ID: {doc_id}]\nContent: {doc}")
        
    return "\n\n---\n\n".join(formatted)

class SaveFactInput(BaseModel):
    fact: str = Field(description="The generic fact or note to save.")
    
@tool("save_fact", args_schema=SaveFactInput)
def save_fact_tool(fact: str):
    """Save a precise fact or note to the Brain Vault for long-term memory."""
    # We call the existing API logic or service to save memory.
    # Since we are inside the backend, we can call a service methods.
    # But usually we need `user_id`. Tools don't natively have context.
    # We will need to bind user_id to the tool when creating the agent.
    return "Error: User context missing from tool execution."

# --- 3. Agent Service ---

class AgentService:
    def __init__(self):
        # Allow overriding provider via settings? for now default to configured.
        pass
        
    async def process_message(
        self, 
        session_id: int, 
        user_id: int, 
        message: str, 
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        
        # 1. Setup Chat History
        chat_history = SQLChatMessageHistory(session_id=str(session_id), user_id=user_id)
        
        # 2. Setup LLM based on requested model
        llm = None
        
        def get_llm(model_name):
            google_key = settings.GEMINI_API_KEY
            
            if "gemini" in model_name.lower():
                if google_key:
                    return ChatGoogleGenerativeAI(
                        google_api_key=google_key, 
                        model=model_name,
                        temperature=temperature, # New param
                        max_output_tokens=max_tokens # New param
                    )
                raise ValueError("Google API Key not configured.")
            elif "gpt" in model_name.lower():
                if settings.OPENAI_API_KEY:
                    return ChatOpenAI(
                        api_key=settings.OPENAI_API_KEY, 
                        model=model_name,
                        temperature=temperature, # New param
                        max_tokens=max_tokens # New param
                    )
                raise ValueError("OpenAI API Key not configured.")
            else:
                if settings.OPENAI_API_KEY: return ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o", temperature=temperature, max_tokens=max_tokens)
                if google_key: return ChatGoogleGenerativeAI(google_api_key=google_key, model="gemini-2.5-flash", temperature=temperature, max_output_tokens=max_tokens)
                raise ValueError("No LLM API keys configured.")

        llm = get_llm(model)
             
        # 3. Setup Tools (Same as before)
        async def save_fact_wrapper(fact: str):
            """Save a fact."""
            from app.models.memory import Memory
            from app.db.session import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                mem = Memory(
                   user_id=user_id,
                   content=fact,
                   title="Agent Fact",
                   source_llm="agent",
                   status="approved",
                   tags=["auto-fact"],
                   show_in_inbox=False
                )
                db.add(mem)
                await db.commit()
                from app.worker import ingest_memory_task
                ingest_memory_task.delay(mem.id, user_id, fact, "Agent Fact", ["auto-fact"], "agent")
            return "Fact saved successfully."

        save_fact_tool_instance = StructuredTool.from_function(
            func=save_fact_wrapper,
            name="save_fact",
            description="Save a fact/note to memory.",
            args_schema=SaveFactInput,
            coroutine=save_fact_wrapper
        )
        
        tools = [search_memory_tool, save_fact_tool_instance]
        
        # 4. Create Agent
        prompt = hub.pull("hwchase17/react")
        
        agent = create_react_agent(llm, tools, prompt)
        # Enable intermediate steps
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True, 
            handle_parsing_errors=True,
            return_intermediate_steps=True # Capture tool usage
        )
        
        # 5. Run
        await chat_history.add_message(HumanMessage(content=message))
        history_messages = await chat_history.aget_messages()
        history_text = "\n".join([f"{m.type}: {m.content}" for m in history_messages[:-1]]) 
        
        final_input = message
        if history_text:
            final_input = f"Previous Conversation:\n{history_text}\n\nCurrent Input: {message}"

        try:
            result = await agent_executor.ainvoke({"input": final_input})
            output = result["output"]
            intermediate_steps = result.get("intermediate_steps", [])
            
            # Extract Sources
            sources = []
            for action, observation in intermediate_steps:
                if action.tool == "search_memory":
                    # Parse the observation string which mimics document content
                    # Format: "Source: Title [ID: 123]\nContent: ..."
                    if isinstance(observation, str) and "Source: " in observation:
                        parts = observation.split("Source: ")
                        for part in parts[1:]:
                            # title_line might look like "My Doc [ID: 5]"
                            title_line = part.split("\nContent:")[0].strip()
                            
                            # Parse ID if present
                            doc_id = None
                            title_text = title_line
                            
                            import re
                            # Check for [ID: ...] pattern
                            id_match = re.search(r"\[ID: (.*?)\]", title_line)
                            if id_match:
                                doc_id = id_match.group(1)
                                title_text = title_line.replace(f"[ID: {doc_id}]", "").strip()
                            
                            source_obj = {"title": title_text, "id": doc_id}
                            
                            # Add if unique by ID (or title if no ID)
                            exists = False
                            for s in sources:
                                if doc_id and s.get("id") == doc_id:
                                    exists = True
                                    break
                                if not doc_id and s.get("title") == title_text:
                                    exists = True
                                    break
                            
                            if not exists:
                                sources.append(source_obj)

            # Save AI Response
            await chat_history.add_message(AIMessage(content=output))
            
            return {
                "output": output,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Agent failed: {e}")
            return {
                "output": "I'm sorry, I encountered an error while thinking.",
                "sources": []
            }

agent_service = AgentService()
