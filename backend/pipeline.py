import json
from model_router import call_llm
from prompts import EXTRACT_PROMPT, VERDICT_PROMPT, REPAIR_PROMPT
from duckduckgo_search import DDGS
import re
import json

def extract_claims(text: str) -> list:
    prompt = EXTRACT_PROMPT.format(text=text)
    raw = call_llm(prompt)
    
    # 1. TRICK: Use Regex to find everything between the first [ and last ]
    # This ignores any "Here is the JSON" conversational text from the AI
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        clean = match.group(0)
    else:
        # Fallback to the old method if regex fails
        clean = raw.strip().replace('```json', '').replace('```', '').strip()
    
    try:
        data = json.loads(clean)
        # 2. Logic to handle both [{"claim":...}] and {"claims": [...]}
        if isinstance(data, dict) and "claims" in data:
            return data["claims"]
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Extraction Error: {e} | Raw Output: {raw[:100]}")
        # 3. Emergency Fallback: If AI fails, manually split by commas for the demo
        return [{"sentence": s.strip(), "subject": "Unknown", "predicate": "is", "object": "Unknown"} 
                for s in text.split(',') if len(s.strip()) > 3]
# 2. Verification Logic
def verify_claim(claim: dict) -> dict:
    query = claim.get('search_query', claim.get('sentence'))
    snippets = "No search results found."
    
    try:
        with DDGS() as ddgs:
            # list() ensures we capture the search results immediately
            search_results = list(ddgs.text(query, max_results=3))
            if search_results:
                snippets = "\n".join([f"Source: {r['href']} | Content: {r['body']}" for r in search_results])
    except Exception as e:
        print(f"DEBUG: Search error: {e}")

    prompt = VERDICT_PROMPT.format(
        claim=claim['sentence'], subject=claim['subject'],
        predicate=claim['predicate'], object=claim['object'],
        snippets=snippets
    )
    
    res = call_llm(prompt)
    clean_res = res.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
    
    try:
        data = json.loads(clean_res)
        verdict_str = str(data.get("verdict", "UNVERIFIABLE")).upper()
        reason_str = str(data.get("reason", "")).upper()
        
        TRUTH_WORDS = ["VERIFIED", "TRUE", "CONFIRMED", "SUPPORTED", "FACTUAL", "PARTIALLY CONFIRMED"]
        LIE_WORDS = ["CONTRADICTED", "FALSE", "INACCURATE", "LIE", "DENIED", "REFUTED", "INCORRECT", "UNSUPPORTED", "MISSING"]

        if any(word in verdict_str for word in LIE_WORDS) or "NOT SUPPORT" in reason_str:
            data["score"] = 0.0
            data["color"] = "#ef4444" 
        elif any(word in verdict_str for word in TRUTH_WORDS):
            data["score"] = 1.0
            data["color"] = "#22c55e" 
        else:
            data["score"] = 0.5
            data["color"] = "#eab308" 
            
        return data
    except:
        return {
            "verdict": "UNVERIFIABLE", 
            "reason": "Parsing error", 
            "source": "",
            "score": 0.5,
            "color": "#eab308"
        }

# 3. Repair Logic
def repair_sentence(item: dict) -> str:
    prompt = REPAIR_PROMPT.format(
        wrong=item.get('sentence', ''),
        source_snippet=item.get('reason', '')
    )
    return call_llm(prompt).strip()

# 4. Scoring Logic
def calculate_document_score(results: list) -> dict:
    if not results: 
        return {"score": 0, "label": "No Data", "color": "#94a3b8"}
    
    total_points = sum(r.get('score', 0.5) for r in results)
    score = int((total_points / len(results)) * 100)
    
    if score > 80:
        label, color = "Highly Credible", "#22c55e"
    elif score > 50:
        label, color = "Mixed Accuracy", "#eab308"
    else:
        label, color = "High-Risk / Misinformation", "#ef4444"
    
    return {"score": score, "label": label, "color": color}
