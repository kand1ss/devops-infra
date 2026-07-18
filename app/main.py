from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(name="My App")
instrumentator = Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health():
    return {"success": True}

