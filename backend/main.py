from fastapi import FastAPI, File, UploadFile
# Use this specific path for the middleware
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
from pipeline import extract_claims, verify_claim, repair_sentence
from utils import extract_text_from_pdf
# CRITICAL: Added 'repair_sentence' to the imports below
from pipeline import extract_claims, verify_claim, repair_sentence, calculate_document_score

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

@app.post("/verify-pdf")
async def verify_pdf(file: UploadFile = File(...)):
    """
    Reads an uploaded PDF, extracts the first 2000 characters, 
    and runs the fact-check pipeline.
    """
    # 1. Read the raw bytes from the uploaded file
    content = await file.read()
    
    # 2. Convert PDF bytes to plain text
    raw_text = extract_text_from_pdf(content)
    
    # 3. Limit text to avoid 'Token Limit' errors with the AI
    sample_text = raw_text[:2000]
    
    # 4. Run your existing verification loop
    claims = extract_claims(sample_text)
    results = []
    for c in claims:
        verdict = verify_claim(c)
        results.append({**c, **verdict})
        
    return {
        "filename": file.filename, 
        "results": results,
        "summary": calculate_document_score(results) # Add this line
    }
