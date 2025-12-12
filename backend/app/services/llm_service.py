from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import google.generativeai as genai
from app.core.config import settings

class LLMService:
    def __init__(self):
        # Initialize with dummy key if not present to avoid startup error, 
        # but requests will fail if key is missing.
        self.openai_api_key = "OPENAI_API_KEY" 
        # In a real app, we'd fetch from settings or user input.
        
    async def generate_response(self, query: str, context: List[str], provider: str = "openai", api_key: Optional[str] = None) -> str:
        if not api_key:
            return "Error: API Key is required."
            
        if not context:
            return "I couldn't find any relevant information in your Brain Vault to answer that. Please try adding more memories or documents related to your specific question."

        context_str = "\n\n".join(context)
        system_prompt = (
            "You are the Brain Vault AI, a personal knowledge assistant. "
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
                # Using gemini-2.5-flash as requested (Year 2025)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                combined = f"{system_prompt}\n\nUser Question: {query}"
                response = model.generate_content(combined)
                return response.text
            except Exception as e:
                return f"Gemini Error: {str(e)}"

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
        # Quick heuristic to avoid burning tokens on tiny content
        if len(content) < 3:
            return {"title": "Short Note", "tags": [], "summary": content}

        try:
            # Check configured provider for background jobs
            # We need a fallback or user provided key. 
            # In the router, we will pass the key.
            target_key = api_key
            if not target_key: 
                print("LLM Service: No API Key provided for metadata extraction")
                return {} 
                
            print(f"LLM Service: Extracting metadata for content (len={len(content)})") 

            import json
            import re
            
            # Context window management for existing tags 
            tag_context_str = ", ".join(existing_tags[:50])
            if len(existing_tags) > 50:
                tag_context_str += "..."
            
            system_instruction = f"""You are the 'Brain Vault' AI archivist.
Analyze the user's content and extract structured metadata.

Required Output (JSON):
{{
    "title": "Concise Title (max 6 words)",
    "summary": "Brief summary (max 2 sentences)",
    "tags": ["tag-1", "tag-2"]
}}

Rules for Tags:
- Generate 3-5 relevant tags.
- Format: lowercase, kebab-case (e.g., "project-management", "react-js").
- PREFER existing tags from the provided context if they match.
- Create new tags only if necessary.
- If content is too short/generic, return minimal tags.

Existing Tags Context:
[{tag_context_str}]"""

            user_message = f"""Content to Analyze:
{content[:4000]}"""
            
            # Generate
            text = ""
            if target_key.startswith("sk-"): # OpenAI
                llm = ChatOpenAI(api_key=target_key, model="gpt-3.5-turbo", temperature=0)
                messages = [
                    SystemMessage(content=system_instruction),
                    HumanMessage(content=user_message)
                ]
                res = await llm.ainvoke(messages)
                text = res.content
            else: # Assume Gemini
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
                        print(f"Gemini 2.5 failed ({e_model}), trying gemini-1.5-flash")
                        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
                        combined_prompt = f"{system_instruction}\n\n{user_message}"
                        res = model.generate_content(combined_prompt)
                        text = res.text
                except Exception as e:
                    print(f"Gemini generation failed: {e}")
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
            
        except Exception as e:
            print(f"Metadata extraction failed: {e}")
            return {}

llm_service = LLMService()
