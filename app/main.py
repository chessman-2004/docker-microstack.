from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
import os
import redis

from database import get_db
import models
from tasks import process_job_task

app = FastAPI(title="Production Microservices API")

Instrumentator().instrument(app).expose(app)

REDIS_HOST = os.getenv("REDIS_HOST", "cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Distributed PDF Generation Engine",
        "version": "4.0.0"
    }

@app.post("/jobs/")
def create_job(task_type: str, db: Session = Depends(get_db)):
    new_job = models.Job(task_type=task_type, status="PENDING")
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    process_job_task.delay(new_job.id)
    r.incr("total_jobs_created")
    
    return {
        "message": "PDF generation task dispatched to Celery worker", 
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

@app.get("/jobs/{job_id}/download")
def download_job_pdf(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "COMPLETED":
        raise HTTPException(status_code=400, detail=f"Job PDF not ready. Current status: {job.status}")
    
    file_path = f"/app/generated_pdfs/report_job_{job.id}.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Generated file not found on volume storage")
    
    return FileResponse(path=file_path, filename=f"report_job_{job.id}.pdf", media_type="application/pdf")

@app.get("/health")
def health_check():
    return {"status": "healthy"}