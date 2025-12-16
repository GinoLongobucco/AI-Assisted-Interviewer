import os
from typing import List, Dict
from openai import OpenAI
import google.generativeai as genai

# Initialize clients
openai_client = None
gemini_model = None

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

# Initialize the appropriate client
if LLM_PROVIDER == "openai":
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY not found in environment")
    else:
        openai_client = OpenAI(api_key=openai_api_key)
        
elif LLM_PROVIDER == "gemini":
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("ERROR: GEMINI_API_KEY not found in environment")
    else:
        genai.configure(api_key=gemini_api_key)
        gemini_model = genai.GenerativeModel('gemini-3-pro-preview')


def call_llm(messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
    """
    Abstraction layer for calling LLM (supports both OpenAI and Gemini)
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Creativity level (0-1)
    
    Returns:
        str: LLM response text
    """
    try:
        if LLM_PROVIDER == "openai":
            if not openai_client:
                raise ValueError("OpenAI client not initialized. Check OPENAI_API_KEY in .env")
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        
        elif LLM_PROVIDER == "gemini":
            if not gemini_model:
                raise ValueError("Gemini model not initialized. Check GEMINI_API_KEY in .env")
            
            # Convert messages to Gemini format
            # Gemini doesn't use system messages in the same way, so we'll combine
            prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt += f"{msg['content']}\n\n"
                elif msg["role"] == "user":
                    prompt += f"{msg['content']}\n"
            
            response = gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                )
            )
            return response.text
        
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")
    
    except Exception as e:
        print(f"ERROR in call_llm: {str(e)}")
        raise
