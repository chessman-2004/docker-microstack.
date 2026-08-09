import time
from celery_app import celery_app
from database import SessionLocal
import models

@celery_app.task(name="process_job_task")
def process_job_task(job_id: int):
    db = SessionLocal()
    try:
        # 1. Fetch job from PostgreSQL
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            return "Job not found"

        # 2. Update status to PROCESSING
        job.status = "PROCESSING"
        db.commit()

        # 3. Simulate heavy workload (e.g. 10 seconds of computation/file rendering)
        time.sleep(10)

        # 4. Mark job as COMPLETED
        job.status = "COMPLETED"
        job.result = f"Successfully processed '{job.task_type}' at job ID {job.id}"
        db.commit()

        return f"Job {job_id} done"
    finally:
        db.close()