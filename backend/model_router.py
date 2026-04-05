import os
import google.generativeai as genai
from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv

# Load API keys from the .env file
load_dotenv()

def call_llm(prompt: str) -> str:
    """
    Routes the prompt to the fastest/most reliable available LLM.
    Always returns a string (expecting a JSON array format for Veritas).
    """
    
    # 1. PRIMARY: Groq (Llama 3.1 - Lightning Fast & highly reliable)
    try:
        client = Groq(api_key=os.getenv('GROQ_KEY'))
        res = client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=[{'role':'user','content':prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        print(f"DEBUG: Groq Failed: {e}")

    # 2. FALLBACK 1: Gemini (With the 404-fix version tag)
    try:
        genai.configure(api_key=os.getenv('GEMINI_KEY_1'))
        # CRITICAL FIX: Using '-001' bypasses the deprecated package 404 error
        model = genai.GenerativeModel('gemini-1.5-flash-001') 
        response = model.generate_content(prompt)
        if response.text:
            return response.text
    except Exception as e:
        print(f"DEBUG: Gemini Failed: {e}")

    # 3. FALLBACK 2: OpenRouter (The "No-Fail" safety net)
    try:
        client = OpenAI(
            api_key=os.getenv('OPENROUTER_KEY'),
            base_url="https://openrouter.ai/api/v1"
        )
        res = client.chat.completions.create(
            model='mistralai/mistral-7b-instruct:free',
            messages=[{'role':'user','content':prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        print(f"DEBUG: OpenRouter Failed: {e}")

    # 4. FINAL FAIL-SAFE: Return an empty JSON array so the pipeline doesn't crash
    return "[]"