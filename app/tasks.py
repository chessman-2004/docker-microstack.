import os
from celery_app import celery_app
from database import SessionLocal
from models import Job
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PDF_STORAGE_DIR = "/app/generated_pdfs"
os.makedirs(PDF_STORAGE_DIR, exist_ok=True)

@celery_app.task(name="tasks.generate_pdf_task")
def generate_pdf_task(job_id: int, task_type: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False

        job.status = "PROCESSING"
        db.commit()

        # Render Real PDF Document via ReportLab
        file_name = f"report_job_{job_id}.pdf"
        file_path = os.path.join(PDF_STORAGE_DIR, file_name)

        c = canvas.Canvas(file_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(100, 750, "Microstack Enterprise Execution Report")
        c.setFont("Helvetica", 12)
        c.drawString(100, 710, f"Job Identification ID: {job_id}")
        c.drawString(100, 690, f"Task Categorization: {task_type}")
        c.drawString(100, 670, "Status: COMPLETED")
        c.drawString(100, 650, "Engine: ReportLab PDF Compilation Subsystem")
        c.save()

        # Update Job Record in PostgreSQL
        job.status = "COMPLETED"
        job.result = f"/jobs/{job_id}/download"
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "FAILED"
            job.result = str(e)
            db.commit()
        raise e
    finally:
        db.close()