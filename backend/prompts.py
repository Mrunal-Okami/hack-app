# prompts.py [cite: 122-133, 154-165, 218-226]
EXTRACT_PROMPT = """
You are a factual claim extractor. 
Analyze the following text and extract every unique factual claim as a separate JSON object.

Text: "{text}"

Return ONLY a JSON list of objects with these keys: "sentence", "subject", "predicate", "object".
Example:
[
  {{"sentence": "The moon is a planet", "subject": "Moon", "predicate": "is", "object": "planet"}},
  {{"sentence": "The moon revolves around Earth", "subject": "Moon", "predicate": "revolves", "object": "Earth"}}
]
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