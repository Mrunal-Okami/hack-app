# prompts.py [cite: 122-133, 154-165, 218-226]

EXTRACT_PROMPT = """
Read the text below. Extract every falsifiable factual claim.
For each claim return a JSON object with these exact keys:
sentence: the exact sentence from the text
subject:  the main subject of the claim
predicate: the action or relationship
object:   the claimed fact/value/date
search_query: a 4-6 word web search to verify this claim
claim_type: FACTUAL, STATISTICAL, TEMPORAL, or OPINION

Return ONLY a valid JSON array. No markdown, no preamble.
TEXT: {text}
"""

VERDICT_PROMPT = """
Claim: {claim}
Evidence from Web: {snippets}

Instructions:
1. If the web evidence clearly confirms or denies the claim, use it.
2. If the web evidence is missing, use your internal verified knowledge to provide a verdict.
3. Be decisive. If you know Narendra Modi is the PM, mark Rahul Gandhi as CONTRADICTED.

Return ONLY JSON: {{"verdict":"...","reason":"...","source":"..."}}
"""

REPAIR_PROMPT = """
The following sentence contains a factual error: {wrong}
Verified source info: {source_snippet}
Rewrite the sentence to be factually correct while keeping the same style.
Return ONLY the corrected sentence.
"""