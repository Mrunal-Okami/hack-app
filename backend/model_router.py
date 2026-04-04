# model_router.py [cite: 35-78]
import os
import google.generativeai as genai
from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def call_llm(prompt: str) -> str:
    # 1. Primary: Gemini (Best reasoning) [cite: 48-54]
    try:
        genai.configure(api_key=os.getenv('GEMINI_KEY_1'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        if response.text:
            return response.text
    except Exception as e:
        print(f"DEBUG: Gemini Failed: {e}")

    # 2. Fallback 1: Groq (Extreme Speed) [cite: 57-64]
    try:
        client = Groq(api_key=os.getenv('GROQ_KEY'))
        res = client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=[{'role':'user','content':prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        print(f"DEBUG: Groq Failed: {e}")

    # 3. Fallback 2: OpenRouter (The "No-Fail" safety net) [cite: 67-74]
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

    # 4. Final Fail-safe: Return a valid empty JSON array so pipeline doesn't crash [cite: 77-78]
    return "[]"