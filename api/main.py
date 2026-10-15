from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.circuit_breaker import CircuitBreaker
from src.idempotency import IdempotencyStore
from src.queue import FileQueue
from src.monitor import Monitor

app = FastAPI(title="Integration Framework")
breakers = {}
idem = IdempotencyStore()
queue = FileQueue()
monitor = Monitor()

class SubmitRequest(BaseModel):
    key: str
    topic: str = "default"
    payload: dict

@app.get("/health")
def health():
    return {"ok": True, "breakers": {k: b.stats() for k, b in breakers.items()}}

@app.post("/breakers/{name}")
def create_breaker(name: str, threshold: int = 5):
    breakers[name] = CircuitBreaker(name, failure_threshold=threshold)
    return breakers[name].stats()

@app.get("/breakers/{name}")
def get_breaker(name: str):
    if name not in breakers:
        raise HTTPException(404, "breaker not found")
    return breakers[name].stats()

@app.post("/submit")
def submit(req: SubmitRequest):
    existing = idem.get(req.key)
    if existing:
        return {"status": "duplicate", "result": existing["result"]}
    msg = queue.enqueue(req.payload, req.topic)
    idem.set(req.key, {"message_id": msg["id"]})
    monitor.increment("submitted", {"topic": req.topic})
    return msg

@app.post("/process")
def process(topic: Optional[str] = None):
    m = queue.dequeue(topic)
    if not m:
        return {"processed": False}
    try:
        queue.ack(m["id"])
        monitor.increment("processed", {"topic": m["topic"]})
        return {"processed": True, "id": m["id"]}
    except Exception as e:
        queue.nack(m["id"], retry=True)
        monitor.increment("failed", {"topic": m["topic"]})
        return {"processed": False, "error": str(e)}

@app.get("/queue/stats")
def queue_stats():
    return queue.stats()

@app.get("/monitor")
def monitor_summary():
    return monitor.summary()
