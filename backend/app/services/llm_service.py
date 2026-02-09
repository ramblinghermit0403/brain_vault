import json
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import google.generativeai as genai
from app.core.config import settings
from app.core.aws_config import AWS_CONFIG
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.services.usage_service import usage_service
import tiktoken

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        return len(text) // 4

class LLMService:
    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None) or getattr(settings, "OPENAI_API_KEY", None)
        self.openai_api_key = self.api_key # Backwards compatibility for now
        
    async def generate_response(self, query: str, context: List[str], provider: str = "openai", api_key: Optional[str] = None, user_id: Optional[int] = None) -> str:
        # if not api_key:
        #    return "Error: API Key is required."
        # Allow missing key to fall through to provider defaults (e.g. Bedrock env vars)
        pass
            
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
            if not api_key:
                # Fallback to Bedrock if OpenAI key missing but user just used default provider
                provider = "bedrock"
            else:
                try:
                    llm = ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo")
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=query)
                    ]
                    response = await llm.ainvoke(messages)
                    
                    # Track Usage
                    if user_id:
                         tokens_in = count_tokens(system_prompt + query)
                         tokens_out = count_tokens(response.content)
                         await usage_service.track_usage(user_id, "openai", "gpt-3.5-turbo", tokens_in, tokens_out)
                         
                    return response.content
                except Exception as e:
                    return f"OpenAI Error: {str(e)}"
        
        # Check 'gemini' block...
        if provider == "gemini":
             if not api_key:
                 provider = "bedrock" # Fallback
             else:
                try:
                    genai.configure(api_key=api_key)
                    # Using gemini-1.5-flash as requested
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    combined = f"{system_prompt}\n\nUser Question: {query}"
                    response = model.generate_content(combined)
                    
                    # Track Usage
                    if user_id:
                         # Gemini doesn't always give token counts in simple response, assume estimate
                         tokens_in = count_tokens(combined)
                         tokens_out = count_tokens(response.text)
                         await usage_service.track_usage(user_id, "gemini", "gemini-1.5-flash", tokens_in, tokens_out)
    
                    return response.text
                except Exception as e:
                     return f"Gemini Error: {str(e)}"

        if provider == "bedrock" or "nova" in provider:
            try:
                # Default to Nova Pro (APAC) if not specified
                model_id = "apac.amazon.nova-pro-v1:0" 
                llm = ChatBedrock(
                    model_id=model_id,
                    model_kwargs={"temperature": 0.7},
                    config=AWS_CONFIG
                )
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=query)
                ]
                response = await llm.ainvoke(messages)
                
                # Track Usage
                if user_id:
                     tokens_in = count_tokens(system_prompt + query)
                     tokens_out = count_tokens(response.content)
                     await usage_service.track_usage(user_id, "bedrock", model_id, tokens_in, tokens_out)

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
        # Log intent immediately to debug "Short Note" issues
        print(f"LLM Service: Extracting metadata for content (len={len(content)})") 

        # Quick heuristic to avoid burning tokens on tiny content
        if len(content) < 3:
            return {"title": "Short Note", "tags": [], "summary": content}
            
        # Check for user key, but allow Fallback to Bedrock (System Credentials)
        target_key = api_key 

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
             llm = ChatBedrock(model_id="apac.amazon.nova-pro-v1:0", model_kwargs={"temperature": 0}, config=AWS_CONFIG)
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
                    # Try gemini-1.5-flash w/ JSON mode
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
                        combined_prompt = f"{system_instruction}\n\n{user_message}"
                        # Check if model supports it (response_mime_type)
                        res = model.generate_content(combined_prompt)
                        text = res.text
                    except Exception as e_model:
                        print(f"Gemini 1.5 failed ({e_model}), trying gemini-1.5-flash fallback")
                        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
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
        
        # 1. Try Bedrock (Nova Pro) First - Always attempt if available
        try:
                # We assume availability of AWS credentials
                llm = ChatBedrock(model_id="apac.amazon.nova-pro-v1:0", model_kwargs={"temperature": 0}, config=AWS_CONFIG)
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
                model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
                res = model.generate_content(f"{system_prompt}\n\n{user_message}")
                text = res.text
            else:
                 raise ValueError("No valid API Key or Bedrock configuration found for chunk enrichment")
            
        import json
        import re
        
        # Clean
        text = text.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Attempt to fix invalid escapes
            try:
                import re
                # Replace backslashes not followed by valid escape chars
                clean_text = re.sub(r'\\(?![/u"\\bfnrt])', r'\\\\', text)
                return json.loads(clean_text)
            except:
                    pass

            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match: 
                try:
                        return json.loads(match.group())
                except:
                        pass
            # If we got text but couldn't parse JSON, that's a failure we should know about
            raise ValueError(f"Failed to parse JSON from LLM response: {text[:100]}...")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def extract_facts_from_text(self, text: str, api_key: Optional[str] = None, reference_date: Optional[datetime] = None) -> List[dict]:
        """
        Extract Atomic Facts (Subject-Predicate-Object) from text.
        """
        if len(text) < 20: 
            return []
            
        target_key = api_key or self.openai_api_key
        
        # Default to today if not provided
        # Default to today if not provided
        if not reference_date:
            reference_date = datetime.now()
            
        # Use Local/User Timezone for "Day" context (e.g. 2023-05-08) instead of UTC (which might be prev day)
        # This matches the user's intuitive understanding of "Today/Yesterday"
        date_str = reference_date.astimezone().strftime('%Y-%m-%d')
        
        system_prompt = f"""You are a Knowledge Graph Extractor.
Extract atomic facts from the text as Subject-Predicate-Object triples, preserving temporal and spatial context.

Context:
Memory Creation Date: {date_str}

Output JSON format:
[
  {{
    "subject": "Melanie",
    "predicate": "painted",
    "object": "a sunrise",
    "location": "on the beach",
    "valid_from": "2023-05-07T10:00:00",
    "confidence": 0.95
  }}
]

Rules:
1. **Atomic**: Break complex sentences into simple triples.
2. **Explicit Subjects**: Do NOT canonicalize to "User" unless strictly necessary. Extract the explicit name of the subject.
3. **Temporal Priority**: 
   - IF the text mentions a specific date (e.g. "on 2024-12-25"), use THAT as the "valid_from".
   - IF the text mentions a relative date (e.g. "yesterday"), calculate it relative to the **Memory Creation Date** ({date_str}).
   - IF NO date is mentioned, use the **Memory Creation Date** as the default "valid_from".
4. **Spatial/Location**: If a location is mentioned ("on the beach", "in New York"), extract it into the "location" field. Do NOT include it in the 'object' if it is extracted here.
5. **Filter**: Only extract meaningful knowledge.
6. **Format**: Output ONLY valid JSON.
"""
        user_message = f"Text to Analyze:\n{text[:2000]}"
        
        try:
            # 1. Try Bedrock (Nova Pro)
            used_bedrock = False
            try:
                llm = ChatBedrock(model_id="apac.amazon.nova-pro-v1:0", model_kwargs={"temperature": 0}, config=AWS_CONFIG)
                messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_message)]
                res = await llm.ainvoke(messages)
                text_response = res.content
                used_bedrock = True
            except Exception as e:
                print(f"Bedrock Fact Extraction Failed: {e}")
                pass
                
            if not used_bedrock:
                # Fallback
                if target_key and target_key.startswith("sk-"):
                    llm = ChatOpenAI(api_key=target_key, model="gpt-3.5-turbo", temperature=0)
                    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_message)]
                    res = await llm.ainvoke(messages)
                    text_response = res.content
                elif target_key: # Gemini
                    genai.configure(api_key=target_key)
                    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
                    res = model.generate_content(f"{system_prompt}\n\n{user_message}")
                    text_response = res.text
                else:
                    return []

            import json
            import re
            
            # Clean
            text_response = text_response.replace("```json", "").replace("```", "").strip()
            
            # DEBUG: Date Resolution Tracking
            print(f"[DEBUG DATE] Ref Date Passed: {reference_date} | Prompt Date Str: {date_str}")
            print(f"[DEBUG DATE] LLM Raw Response: {text_response[:200]}...") # Peek start

            try:
                data = json.loads(text_response)
                if isinstance(data, list):
                    return data
                return []
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error in Fact Extraction. Raw response: {text_response[:500]}... Error: {e}")
                try:
                    # Robust extraction: Find the first '[' and the last ']'
                    match = re.search(r'\[.*\]', text_response, re.DOTALL)
                    if match:
                        potential_json = match.group()
                        return json.loads(potential_json)
                except Exception as inner_e:
                    print(f"Regex Fallback Failed: {inner_e}")
                return []
            
        except Exception as e:
            print(f"Fact extraction failed: {e}")
            return []

    async def generate_chat_title(self, conversation_context: str, api_key: Optional[str] = None) -> str:
        """
        Generate a concise (3-6 words) title for a chat session.
        """
        target_key = api_key or self.api_key
        
        system_prompt = (
            "You are a helpful assistant that generates concise titles for chat sessions. "
            "Generate a short, descriptive title (maximum 6 words) for the provided conversation start. "
            "Do not use quotes or prefixes like 'Title:'. Just the text."
        )
        
        try:
             # 1. Try Bedrock First (Unconditionally)
            try:
                 llm = ChatBedrock(model_id="apac.amazon.nova-pro-v1:0", model_kwargs={"temperature": 0.7}, config=AWS_CONFIG)
                 messages = [SystemMessage(content=system_prompt), HumanMessage(content=conversation_context)]
                 res = await llm.ainvoke(messages)
                 return res.content.strip()
            except Exception as e:
                 print(f"Bedrock title gen failed: {e}")
                 # Continue to fallbacks

            if not target_key:
                print("Title Generation: Bedrock failed and no API Key found.")
                return "New Chat"

            if target_key.startswith("sk-"):
                llm = ChatOpenAI(api_key=target_key, model="gpt-3.5-turbo", temperature=0.7)
                messages = [SystemMessage(content=system_prompt), HumanMessage(content=conversation_context)]
                res = await llm.ainvoke(messages)
                return res.content.strip()
            # Gemini
            else:
                if target_key: genai.configure(api_key=target_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"{system_prompt}\n\nConversation:\n{conversation_context}")
                return res.text.strip()
        except Exception as e:
            print(f"Title generation failed: {e}")
            return "New Chat"

llm_service = LLMService()
