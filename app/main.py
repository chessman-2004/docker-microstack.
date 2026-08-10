import os
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Job
from tasks import generate_pdf_task, PDF_STORAGE_DIR
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Enterprise Microstack API", version="2.0.0")

# Enable Prometheus Telemetry
Instrumentator().instrument(app).expose(app)

@app.get("/health")
def healthcheck():
    return {"status": "healthy", "architecture": "cloud-native-k8s"}

@app.post("/jobs/", status_code=202)
def create_job(task_type: str = Query("enterprise_pdf_generation"), db: Session = Depends(get_db)):
    job = Job(task_type=task_type, status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)

    # Dispatch to Celery Background Worker
    generate_pdf_task.delay(job.id, task_type)

    return {
        "message": "PDF generation task dispatched to Celery worker",
        "job_id": job.id,
        "status": job.status
    }

@app.get("/jobs/")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.id.desc()).all()
    return {
        "total_jobs_queued": str(len(jobs)),
        "jobs": [
            {
                "id": j.id,
                "task_type": j.task_type,
                "status": j.status,
                "result": j.result,
                "created_at": j.created_at.isoformat() if j.created_at else None
            }
            for j in jobs
        ]
    }

@app.get("/jobs/{job_id}/download")
def download_pdf(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or job.status != "COMPLETED":
        raise HTTPException(status_code=404, detail="Job not found or PDF compilation incomplete")

    file_path = os.path.join(PDF_STORAGE_DIR, f"report_job_{job_id}.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF asset file missing on disk storage")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"enterprise_report_{job_id}.pdf"
    )