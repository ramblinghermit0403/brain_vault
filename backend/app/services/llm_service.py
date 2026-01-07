from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
import google.generativeai as genai
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None) or getattr(settings, "OPENAI_API_KEY", None)
        self.openai_api_key = self.api_key # Backwards compatibility for now
        
    async def generate_response(self, query: str, context: List[str], provider: str = "openai", api_key: Optional[str] = None) -> str:
        if not api_key:
            return "Error: API Key is required."
            
        if not context:
            return "I couldn't find any relevant information in your MemWyre to answer that. Please try adding more memories or documents related to your specific question."

        context_str = "\n\n".join(context)
        system_prompt = (
            "You are the MemWyre AI, a personal knowledge assistant. "
            "Use ONLY the following Context to answer the user's question. "
            "If the answer is not explicitly supported by the Context, state that you do not have enough information. "
            "Do not hallucinate or use outside knowledge unless it is general definitions to help explain the context.\n\n"
            f"Context:\n{context_str}"
        )
        
        if provider == "openai":
            try:
                llm = ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo")
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=query)
                ]
                response = await llm.ainvoke(messages)
                return response.content
            except Exception as e:
                return f"OpenAI Error: {str(e)}"

        elif provider == "gemini":
            try:
                genai.configure(api_key=api_key)
                # Using gemini-2.5-flash as requested
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                combined = f"{system_prompt}\n\nUser Question: {query}"
                response = model.generate_content(combined)
                return response.text
            except Exception as e:
                return f"Gemini Error: {str(e)}"

        elif provider == "bedrock" or "nova" in provider:
            try:
                # Default to Nova Pro (APAC) if not specified
                model_id = "apac.amazon.nova-pro-v1:0" 
                llm = ChatBedrock(
                    model_id=model_id,
                    model_kwargs={"temperature": 0.7}
                )
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=query)
                ]
                response = await llm.ainvoke(messages)
                return response.content
            except Exception as e:
                return f"Bedrock Error: {str(e)}"

        elif provider == "claude":
            # Placeholder for Claude integration
            return "Claude integration not yet implemented."
        else:
            return "Unsupported provider."

    async def extract_metadata(self, content: str, existing_tags: List[str] = [], api_key: Optional[str] = None) -> dict:
        """
        Extract Title, Summary, and Tags from content using LLM.
        """
        # Quick heuristic to avoid burning tokens on tiny content
        if len(content) < 3:
            return {"title": "Short Note", "tags": [], "summary": content}
            
        # Check for user key, but allow Fallback to Bedrock (System Credentials)
        target_key = api_key
        
        # Log intent
        print(f"LLM Service: Extracting metadata for content (len={len(content)})") 

        import json
        import re
        
        # Context window management for existing tags 
        tag_context_str = ", ".join(existing_tags[:50])
        if len(existing_tags) > 50:
            tag_context_str += "..."
        
        system_instruction = f"""You are the 'MemWyre' AI archivist.
Analyze the user's content and extract structured metadata.

Required Output (JSON):
{{
    "title": "Concise Title (max 6 words)",
    "summary": "Brief summary (max 2 sentences)",
    "tags": ["tag-1", "tag-2"]
}}

Rules for Tags:
1. **Identify Named Entities**: Extract specific People, Organizations, Locations, Events, and Software/Tools.
   - Examples: "Sam Altman", "OpenAI", "Paris", "WWDC 2024", "PostgreSQL".
2. **Identify Core Topics**: Add 1-2 high-level topics if applicable.
   - Examples: "artificial-intelligence", "meeting-notes".
3. **Format**:
   - Use lowercase, kebab-case for generic topics (e.g., "machine-learning").
   - **Keep proper capitalization and spacing for Named Entities** to distinguish them (e.g., "Sam Altman" NOT "sam-altman", "OpenAI" NOT "openai").
   - Return a flat list of strings mixing both entities and topics.
4. **Context**: PREFER existing tags from the provided context if they match.
5. **Quantity**: Aim for 3-7 high-quality tags.

Existing Tags Context:
[{tag_context_str}]"""

        user_message = f"""Content to Analyze:
{content[:4000]}"""
        
        # Generate
        text = ""
        
        # 1. Try Bedrock (Nova Pro) First - Preferred and often System Configured
        used_bedrock = False
        try:
             # Default to Nova Pro
             llm = ChatBedrock(model_id="apac.amazon.nova-pro-v1:0", model_kwargs={"temperature": 0})
             messages = [
                 SystemMessage(content=system_instruction),
                 HumanMessage(content=user_message)
             ]
             res = await llm.ainvoke(messages)
             text = res.content
             used_bedrock = True
        except Exception as e:
             # Only print error if we have no other fallback or for debugging
             # print(f"Bedrock metadata extraction failed: {e}")
             pass
        
        if not used_bedrock:
            if not target_key:
                 print("LLM Service: Bedrock failed and no API Key provided for fallback.")
                 return {} # No way to proceed

            if target_key.startswith("sk-"): # OpenAI
                llm = ChatOpenAI(api_key=target_key, model="gpt-3.5-turbo", temperature=0)
                messages = [
                    SystemMessage(content=system_instruction),
                    HumanMessage(content=user_message)
                ]
                res = await llm.ainvoke(messages)
                text = res.content
            elif target_key: # Assume Gemini
                genai.configure(api_key=target_key)
                try:
                    # Try gemini-2.5-flash w/ JSON mode
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
                        combined_prompt = f"{system_instruction}\n\n{user_message}"
                        # Check if model supports it (response_mime_type)
                        res = model.generate_content(combined_prompt)
                        text = res.text
                    except Exception as e_model:
                        print(f"Gemini 2.5 failed ({e_model}), trying gemini-2.5-flash fallback")
                        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
                        combined_prompt = f"{system_instruction}\n\n{user_message}"
                        res = model.generate_content(combined_prompt)
                        text = res.text
                except Exception as e:
                    print(f"Gemini generation failed: {e}")
                    return {}
            else: 
                 return {}

            # Clean JSON
            text = text.replace("```json", "").replace("```", "").strip()
            print(f"LLM Raw Response: {text}")
            
            try:
                data = json.loads(text)
                print(f"LLM Service: Parsed Data: {data}")
                return data
            except json.JSONDecodeError:
                print(f"LLM Service: JSON Decode Error. Raw: {text}")
                # Fallback: try to extract JSON substring if mixed with text
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group())
                    except:
                        pass
                return {}

    async def generate_chunk_enrichment(self, content: str, api_key: Optional[str] = None) -> dict:
        """
        Generate summary, Q&A, and entities for a text chunk.
        """
        if len(content) < 50:
            return {}
            
        target_key = api_key or self.openai_api_key
        # Heuristic: use openai key if available, else assume gemini configured globally or pass explicitly
        
        system_prompt = """You are a precise data enricher for RAG systems.
Analyze the provided text chunk and generate the following JSON output:

{
    "summary": "1-2 sentence extractive summary of the key facts.",
    "generated_qas": [
        {"q": "Question 1?", "a": "Short answer 1."},
        {"q": "Question 2?", "a": "Short answer 2."}
    ],
    "entities": ["Entity1", "Entity2"]
}

Rules:
- Questions should be specific and answerable from the chunk.
- Entities should be specific (Person, Org, Product, Location).
- Keep JSON valid and minimal."""

        user_message = f"Chunk Content:\n{content[:2000]}"
        
        try:
            used_bedrock = False
            # 1. Try Bedrock (Nova Pro) First - Always attempt if available
            try:
                 # We assume availability of AWS credentials
                 llm = ChatBedrock(model_id="apac.amazon.nova-pro-v1:0", model_kwargs={"temperature": 0})
                 messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_message)]
                 res = await llm.ainvoke(messages)
                 text = res.content
                 used_bedrock = True
            except Exception as e:
                 # Only print if we expected it to work or for debugging
                 # print(f"Bedrock chunk enrichment failed: {e}")
                 pass

            if not used_bedrock:
                # Fallback to configured keys
                if target_key and target_key.startswith("sk-"):
                    llm = ChatOpenAI(api_key=target_key, model="gpt-3.5-turbo", temperature=0)
                    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_message)]
                    res = await llm.ainvoke(messages)
                    text = res.content
                elif target_key:
                    # Gemini
                    genai.configure(api_key=target_key)
                    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
                    res = model.generate_content(f"{system_prompt}\n\n{user_message}")
                    text = res.text
                else:
                    return {}
                
            import json
            import re
            
            # Clean
            text = text.replace("```json", "").replace("```", "").strip()
            
            try:
                return json.loads(text)
            except:
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match: return json.loads(match.group())
                return {}
                
        except Exception as e:
            print(f"Chunk enrichment failed: {e}")
            return {}

    async def generate_chat_title(self, conversation_context: str, api_key: Optional[str] = None) -> str:
        """
        Generate a concise (3-6 words) title for a chat session.
        """
        target_key = api_key or self.api_key
        
        if not target_key:
            print("Title Generation: No API Key found.")
            return "New Chat"
        
        system_prompt = (
            "You are a helpful assistant that generates concise titles for chat sessions. "
            "Generate a short, descriptive title (maximum 6 words) for the provided conversation start. "
            "Do not use quotes or prefixes like 'Title:'. Just the text."
        )
        
        try:
            used_bedrock = False
            # 1. Try Bedrock
            if not target_key or (len(target_key) < 10):
                try:
                     llm = ChatBedrock(model_id="apac.amazon.nova-pro-v1:0", model_kwargs={"temperature": 0.7})
                     messages = [SystemMessage(content=system_prompt), HumanMessage(content=conversation_context)]
                     res = await llm.ainvoke(messages)
                     return res.content.strip()
                except Exception as e:
                     print(f"Bedrock title gen failed: {e}")

            if target_key and target_key.startswith("sk-"):
                llm = ChatOpenAI(api_key=target_key, model="gpt-3.5-turbo", temperature=0.7)
                messages = [SystemMessage(content=system_prompt), HumanMessage(content=conversation_context)]
                res = await llm.ainvoke(messages)
                return res.content.strip()
            else:
                # Gemini
                if target_key: genai.configure(api_key=target_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                res = model.generate_content(f"{system_prompt}\n\nConversation:\n{conversation_context}")
                return res.text.strip()
        except Exception as e:
            print(f"Title generation failed: {e}")
            return "New Chat"

llm_service = LLMService()
