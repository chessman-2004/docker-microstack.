from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
import os
import redis

from database import get_db
import models
from tasks import process_job_task

app = FastAPI(title="Production Microservices API")

# Expose Prometheus metrics endpoint
Instrumentator().instrument(app).expose(app)

REDIS_HOST = os.getenv("REDIS_HOST", "cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Distributed Job Engine API",
        "version": "3.0.0"
    }

@app.post("/jobs/")
def create_job(task_type: str, db: Session = Depends(get_db)):
    new_job = models.Job(task_type=task_type, status="PENDING")
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # Dispatch background task to Celery
    process_job_task.delay(new_job.id)
    
    r.incr("total_jobs_created")
    
    return {
        "message": "Job queued for background processing", 
        "job_id": new_job.id,
        "status": "PENDING"
    }

@app.get("/jobs/")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    total_cached = r.get("total_jobs_created") or 0
    return {
        "total_jobs_queued": total_cached,
        "jobs": jobs
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}