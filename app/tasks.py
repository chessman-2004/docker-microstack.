import os
import datetime
from celery_app import celery_app
from database import SessionLocal
import models

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUTPUT_DIR = "/app/generated_pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@celery_app.task(name="process_job_task")
def process_job_task(job_id: int):
    db = SessionLocal()
    try:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            return "Job not found"

        job.status = "PROCESSING"
        db.commit()

        # 1. Generate PDF document path
        file_name = f"report_job_{job.id}.pdf"
        file_path = os.path.join(OUTPUT_DIR, file_name)

        # 2. Render PDF Report via ReportLab
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Document Header
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=12
        )
        story.append(Paragraph("System Intelligence Report", title_style))
        story.append(Paragraph(f"Generated on: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", styles['Normal']))
        story.append(Spacer(1, 15))

        # Job Metadata Table
        data = [
            ["Metric", "Value"],
            ["Job ID", str(job.id)],
            ["Task Type", str(job.task_type)],
            ["Status", "COMPLETED"],
            ["Worker Execution Engine", "Celery Distributed Worker"],
            ["Database Target", "PostgreSQL 15"]
        ]

        table = Table(data, colWidths=[200, 250])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3F4F6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D1D5DB')),
        ]))
        story.append(table)

        doc.build(story)

        # 3. Mark job as COMPLETED and store the relative file path
        job.status = "COMPLETED"
        job.result = f"/jobs/{job.id}/download"
        db.commit()

        return f"Job {job_id} successfully compiled PDF to {file_path}"
    
    except Exception as e:
        job.status = "FAILED"
        job.result = str(e)
        db.commit()
        raise e
    finally:
        db.close()