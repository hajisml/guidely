from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import documents

app = FastAPI(title="Guidely API")

app.include_router(documents.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}
