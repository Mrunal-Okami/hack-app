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
            results = results or []
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
        data = json.loads(clean_res)
        
        # --- NEW HEATMAP LOGIC ---
        verdict = data.get("verdict", "UNVERIFIABLE")
        
        if verdict == "VERIFIED":
            data["score"] = 1.0
            data["color"] = "#22c55e" # Tailwind Green-500
        elif verdict == "CONTRADICTED":
            data["score"] = 0.0
            data["color"] = "#ef4444" # Tailwind Red-500
        else:
            data["score"] = 0.5
            data["color"] = "#eab308" # Tailwind Yellow-500
            
        return data
    except:
        # Fallback for parsing errors
        return {
            "verdict": "UNVERIFIABLE", 
            "reason": "Parsing error", 
            "source": "",
            "score": 0.5,
            "color": "#eab308"
        }
# --- ADD THIS NEW FUNCTION BELOW ---
def repair_sentence(item: dict) -> str:
    """Uses the verified reason to rewrite the lie into a truth."""
    prompt = REPAIR_PROMPT.format(
        wrong=item['sentence'],
        source_snippet=item.get('reason', '')
    )
    return call_llm(prompt).strip()
    
def calculate_document_score(results: list) -> dict:
    if not results: 
        return {"score": 0, "label": "No Data", "color": "#94a3b8"}
    
    # Calculate average confidence across all results
    total_points = sum(r.get('score', 0.5) for r in results)
    score = int((total_points / len(results)) * 100)
    
    if score > 80:
        label, color = "Highly Credible", "#22c55e"
    elif score > 50:
        label, color = "Mixed Accuracy", "#eab308"
    else:
        label, color = "High-Risk / Misinformation", "#ef4444"
    
    return {"score": score, "label": label, "color": color}