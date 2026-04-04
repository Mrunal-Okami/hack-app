# backend/transcriber.py
from faster_whisper import WhisperModel
import torch

# Your check proved this is True, so we force CUDA
device = "cuda"

# 'float16' is the secret for RTX 30-series speed
model = WhisperModel("small", device=device, compute_type="float16")

def transcribe_audio(file_path: str) -> str:
    segments, info = model.transcribe(file_path, beam_size=5)
    text = " ".join([segment.text for segment in segments])
    return text.strip()