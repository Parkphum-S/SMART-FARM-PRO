from fastapi import FastAPI

app = FastAPI(title="Smart Farm Gateway")

@app.get("/health")
def health():
    return {"status": "ok"}
