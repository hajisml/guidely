# Guidely

Internal knowledge assistant. Ask a question in plain language, get a short answer with the sources it came from.

Stack: React + Vite frontend, FastAPI backend. Documents get chunked, embedded and stored in a FAISS index, then Gemini drafts answers from the retrieved chunks.

## Setup

WIP, proper instructions coming once the pipeline works.

```sh
# backend
cd backend
pip install -r ../requirements.txt
uvicorn main:app --reload

# frontend
cd frontend
npm install
npm run dev
```
