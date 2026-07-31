from fastapi import FastAPI

app = FastAPI(title="Guidely API")


@app.get("/health")
def health():
    return {"status": "ok"}
