from fastapi import FastAPI

app = FastAPI(title="Smart Farm Backend")

@app.get("/health")
def health():
    return {"status": "ok"}
