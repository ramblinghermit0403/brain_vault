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
from langchain_aws import ChatBedrock
from langgraph.prebuilt import create_react_agent


# App Imports
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.chat import ChatMessage, ChatSession, MessageRole
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store
from app.services.retrieval_service import retrieval_service
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

    async def add_message(self, message: BaseMessage) -> int:
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
            await db.refresh(db_msg)
            return db_msg.id
            
    async def clear(self) -> None:
        pass

# --- 2. Tools ---



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
            elif "nova" in model_name.lower():
                return ChatBedrock(
                    model_id="apac.amazon.nova-pro-v1:0",
                    model_kwargs={"temperature": temperature, "maxTokens": max_tokens}
                )
            else:
                if settings.OPENAI_API_KEY: return ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o", temperature=temperature, max_tokens=max_tokens)
                if google_key: return ChatGoogleGenerativeAI(google_api_key=google_key, model="gemini-2.5-flash", temperature=temperature, max_output_tokens=max_tokens)
                # Fallback check for Bedrock Nova if configured via implicit Boto3 env vars
                try:
                    return ChatBedrock(model_id="apac.amazon.nova-pro-v1:0", model_kwargs={"temperature": temperature})
                except:
                    pass
                    
                raise ValueError("No LLM API keys configured.")

        llm = get_llm(model)
             
        # 3. Setup Tools
        
        # 3.1 Search Tool (DynamicWrapper)
        class SearchMemoryInput(BaseModel):
             query: str = Field(description="The query to search for in the brain vault.")
             
        async def search_memory_wrapper(query: str):
            """Search for relevant memories."""
            from app.services.retrieval_service import retrieval_service
            from app.db.session import AsyncSessionLocal
            
            async with AsyncSessionLocal() as db:
                results = await retrieval_service.search_memories(
                    query=query,
                    user_id=user_id,
                    db=db,
                    top_k=5
                )
            
            if not results:
                return "No relevant memories found."
            
            formatted = []
            for res in results:
                # Format: Source: Title [ID: 123]\nContent: ...
                meta = res["metadata"]
                doc_id = meta.get("memory_id") or meta.get("document_id") or "unknown"
                title = meta.get("title", "Untitled")
                content = res["text"]
                
                # Append enrichment info if available
                if meta.get("summary"):
                     content = f"Summary: {meta['summary']}\nDetails: {content}"
                
                formatted.append(f"Source: {title} [ID: {doc_id}]\nContent: {content}")
                
            return "\n\n---\n\n".join(formatted)

        search_memory_tool_instance = StructuredTool.from_function(
            func=search_memory_wrapper,
            name="search_memory",
            description="Search for relevant memories, notes, and documents in the Brain Vault.",
            args_schema=SearchMemoryInput,
            coroutine=search_memory_wrapper
        )
        
        # 3.2 Save Tool
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
        
        tools = [search_memory_tool_instance, save_fact_tool_instance]
        
        # 4. Create Agent (LangGraph)
        # This creates a compiled state graph (Runnable)
        app = create_react_agent(llm, tools)
        
        # 5. Prepare Input for LangGraph
        
        # 5.0 Update History with User Message
        await chat_history.add_message(HumanMessage(content=message))
        history_messages = await chat_history.aget_messages()
        
        # 5.1 PRE-FETCH CONTEXT (Smart RAG)
        # Instead of waiting for tool use, we proactively fetch relevant context
        # This gives the agent "reasoning text" immediately.
        context_str = ""
        try:
            # We need a db session for retrieval
            async with AsyncSessionLocal() as db:
                # Top k=3 for immediate context
                results = await retrieval_service.search_memories(
                    query=message,
                    user_id=user_id,
                    db=db,
                    top_k=3
                )
                if results:
                    formatted_ctx = []
                    for res in results:
                        meta = res["metadata"]
                        title = meta.get("title", "Untitled")
                        # Include summary if available for denser context
                        content = res["text"]
                        if meta.get("summary"):
                             content = f"Summary: {meta['summary']}\nDetails: {content}"
                        formatted_ctx.append(f"Source: {title}\nContent: {content}")
                    
                    if formatted_ctx:
                        context_str = "\n\n=== RELEVANT MEMORY CONTEXT ===\n" + "\n---\n".join(formatted_ctx) + "\n=============================\n"
        except Exception as e:
            logger.error(f"Context pre-fetch failed: {e}")

        # Define System Instruction
        instruction = (
            "You are a helpful assistant with access to a Brain Vault memory. "
            "1. If the user asks a question or asks to recall/search, USE 'search_memory' to find the answer and PROVIDE THE ANSWER directly. Do NOT save facts about the search itself. "
            "2. If the user provides NEW facts, notes, or memories to store, call 'save_fact' for each discrete item. "
            "3. If the user asks to 'recall' or 'retrieve', your primary job is to SEARCH and ANSWER, not to save."
        )

        # "instruction" acts as the System Prompt
        # We append the context to the system instruction so the agent "knows" it.
        final_instruction = instruction + context_str
        instruction_msg = SystemMessage(content=final_instruction)
        
        # history_messages already includes the current user message (added at L245)
        input_messages = [instruction_msg] + history_messages
        
        try:
            # invoke returns a dict with keys like 'messages' (list of BaseMessage)
            result = await app.ainvoke({"messages": input_messages})
            
            # Extract final response from the last AI message
            messages_out = result.get("messages", [])
            output = ""
            if messages_out and isinstance(messages_out[-1], AIMessage):
                output = messages_out[-1].content
            else:
                output = "No response generated."

            # Extract Sources from tool executions in message history
            sources = []
            # We scan messages for ToolMessage or AIMessage with tool_calls
            # But our specific source logic relied on "observation" strings from "search_memory"
            # In LangGraph, tool outputs are ToolMessages.
            from langchain_core.messages import ToolMessage
            
            for msg in messages_out:
                if isinstance(msg, ToolMessage) and msg.name == "search_memory":
                    observation = msg.content
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

            # Save AI Response and get ID
            ai_message_id = await chat_history.add_message(AIMessage(content=output))
            
            return {
                "output": output,
                "sources": sources,
                "message_id": ai_message_id
            }
            
        except Exception as e:
            logger.error(f"Agent failed: {e}")
            return {
                "output": "I'm sorry, I encountered an error while thinking.",
                "sources": []
            }

agent_service = AgentService()
