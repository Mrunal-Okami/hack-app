# 🛡️ Veritas AI: Agentic Fact-Verification Engine

**Veritas AI** is a high-performance backend system designed to combat digital misinformation. It uses a multi-model agentic pipeline to extract, verify, and repair factual inconsistencies in raw text and PDF documents.

---

## 🌟 Core Features

* **Multi-Model Verification**: Leverages **Gemini 1.5** for deep reasoning and **Groq (Llama 3)** for lightning-fast processing.
* **PDF Document Auditing**: Uses `pypdf` to parse complex documents and verify embedded claims against real-time web data.
* **Live Web Grounding**: Integrated with **DuckDuckGo Search** to fetch the latest news and official records (NIST, ISRO, etc.).
* **AI-Powered Repair**: Automatically rewrites contradicted sentences into factually accurate versions while maintaining original tone.

---

## 🏗️ System Architecture



The system follows a three-stage pipeline:
1.  **Extraction**: AI identifies testable "Claims" (Subject-Predicate-Object triplets).
2.  **Research**: An autonomous agent generates search queries and fetches web snippets.
3.  **Verdict**: A final model compares snippets to claims and issues a `VERIFIED`, `CONTRADICTED`, or `UNVERIFIABLE` status.

---

## 🚀 Installation & Setup

### 1. Prerequisites
* Python 3.10+
* API Keys for Google Gemini and Groq Cloud.

### 2. Installation
```bash
# Clone the repository
git clone [https://github.com/Mrunal-Okami/hack-app.git](https://github.com/Mrunal-Okami/hack-app.git)
cd hack-app

# Set up virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows (PowerShell)

# Install dependencies
pip install -r requirements.txt