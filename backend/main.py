from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# CRITICAL: Added 'repair_sentence' to the imports below
from pipeline import extract_claims, verify_claim, repair_sentence

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA MODELS ---

class TextData(BaseModel):
    text: str

# New model for the Repair feature
class RepairRequest(BaseModel):
    sentence: str
    reason: str

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "Veritas AI Backend Online"}

@app.post("/verify")
async def process_text(data: TextData):
    claims = extract_claims(data.text)
    results = []
    for c in claims:
        verdict = verify_claim(c)
        results.append({**c, **verdict})
    return {"results": results}

@app.post("/repair")
async def repair_text(data: RepairRequest):
    """
    Takes a wrong sentence and a verification reason, 
    then returns a factually corrected version.
    """
    # We pass the data to the pipeline logic you wrote earlier
    repaired_version = repair_sentence({
        "sentence": data.sentence,
        "reason": data.reason
    })
    return {"repaired": repaired_version}