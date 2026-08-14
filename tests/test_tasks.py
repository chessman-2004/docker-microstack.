import os
import pytest
from tasks import generate_pdf_task, _mark_job_failed
from models import Job
from database import SessionLocal

def test_generate_pdf_task_execution(tmp_path, mocker):
    # Override storage directory to temporary path
    mocker.patch("tasks.PDF_STORAGE_DIR", str(tmp_path))
    
    # Create test job in DB
    db = SessionLocal()
    job = Job(task_type="test_invoice", status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id
    db.close()

    # Execute celery task synchronously
    pdf_path = generate_pdf_task(job_id=job_id, payload=None, request_id="test-req-123")

    # Assert PDF file was created on disk
    assert os.path.exists(pdf_path)
    
    # Assert DB status updated to COMPLETED
    db = SessionLocal()
    updated_job = db.query(Job).filter(Job.id == job_id).first()
    assert updated_job.status == "COMPLETED"
    db.close()

def test_mark_job_failed():
    db = SessionLocal()
    job = Job(task_type="fail_test", status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id
    db.close()

    _mark_job_failed(job_id, "Simulated worker error")

    db = SessionLocal()
    failed_job = db.query(Job).filter(Job.id == job_id).first()
    assert failed_job.status == "FAILED"
    assert "Simulated worker error" in failed_job.result
    db.close()