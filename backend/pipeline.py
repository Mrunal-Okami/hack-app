# backend/pipeline.py
import json
from model_router import call_llm
from prompts import EXTRACT_PROMPT, VERDICT_PROMPT, REPAIR_PROMPT # Added REPAIR_PROMPT
from ddgs import DDGS
def extract_claims(text: str) -> list:
    prompt = EXTRACT_PROMPT.format(text=text)
    raw = call_llm(prompt)
    
    # Cleans up the AI's markdown formatting
    clean = raw.strip().replace('```json', '').replace('```', '').strip()
    
    try:
        data = json.loads(clean)
        # If the AI returns a dictionary with a 'claims' key, extract that list
        if isinstance(data, dict) and "claims" in data:
            return data["claims"]
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Extraction Error: {e}")
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
        
       # --- ROBUST PRECISION HEATMAP LOGIC ---
        verdict_str = str(data.get("verdict", "UNVERIFIABLE")).upper()
        reason_str = str(data.get("reason", "")).upper()
        
        # 1. Keywords that mean the claim is correct
        TRUTH_WORDS = ["VERIFIED", "TRUE", "CONFIRMED", "SUPPORTED", "FACTUAL", "PARTIALLY CONFIRMED"]
        
        # 2. Keywords that mean the claim is wrong or missing evidence
        LIE_WORDS = ["CONTRADICTED", "FALSE", "INACCURATE", "LIE", "DENIED", "REFUTED", "INCORRECT", "UNSUPPORTED", "MISSING"]

        # CRITICAL: Check for LIE_WORDS first, and also scan the 'reason' for negative phrases
        if any(word in verdict_str for word in LIE_WORDS) or "NOT SUPPORT" in reason_str:
            data["score"] = 0.0
            data["color"] = "#ef4444" # Red
        elif any(word in verdict_str for word in TRUTH_WORDS):
            data["score"] = 1.0
            data["color"] = "#22c55e" # Green
        else:
            # This handles "UNVERIFIABLE", "Parsing error", or "OPINION"
            data["score"] = 0.5
            data["color"] = "#eab308" # Yellow
            
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