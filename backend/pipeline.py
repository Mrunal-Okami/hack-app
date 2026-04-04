# backend/pipeline.py
import json
from model_router import call_llm
from prompts import EXTRACT_PROMPT, VERDICT_PROMPT, REPAIR_PROMPT # Added REPAIR_PROMPT
from duckduckgo_search import DDGS

def extract_claims(text: str) -> list:
    prompt = EXTRACT_PROMPT.format(text=text)
    raw = call_llm(prompt)
    clean = raw.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
    try:
        return json.loads(clean)
    except:
        return []

def verify_claim(claim: dict) -> dict:
    query = claim.get('search_query', claim.get('sentence'))
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            # CRITICAL FIX: Include the 'href' (the link) so the AI can use it as a source
            snippets = "\n".join([f"Source: {r['href']} | Content: {r['body']}" for r in results])
    except:
        snippets = "No search results found."

    prompt = VERDICT_PROMPT.format(
        claim=claim['sentence'], subject=claim['subject'],
        predicate=claim['predicate'], object=claim['object'],
        snippets=snippets
    )
    res = call_llm(prompt)
    clean_res = res.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
    try:
        # If the AI returns JSON, this will now include the real source URL from 'snippets'
        return json.loads(clean_res)
    except:
        return {"verdict": "UNVERIFIABLE", "reason": "Parsing error", "source": ""}

# --- ADD THIS NEW FUNCTION BELOW ---
def repair_sentence(item: dict) -> str:
    """Uses the verified reason to rewrite the lie into a truth."""
    prompt = REPAIR_PROMPT.format(
        wrong=item['sentence'],
        source_snippet=item.get('reason', '')
    )
    return call_llm(prompt).strip()

# Example of a robust verify_claim in pipeline.py
def verify_claim(claim: dict) -> dict:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(claim.get('search_query', ''), max_results=3))
            # ... rest of your logic ...
    except Exception as e:
        print(f"Search Error: {e}")
        return {"verdict": "UNVERIFIABLE", "reason": "Search engine timeout", "source": ""}