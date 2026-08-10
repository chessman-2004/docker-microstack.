import os
import logging
from datetime import datetime, timedelta
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from database import SessionLocal
from models import Job

PDF_STORAGE_DIR = "/app/generated_pdfs"
celery_app = Celery("tasks", broker=os.getenv("CELERY_BROKER_URL", "redis://cache:6379/0"))
logger = logging.getLogger(__name__)


def _mark_job_failed(job_id: str, error_reason: str):
    """Fail-safe logger that records job failures directly in Postgres."""
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "FAILED"
            job.result = error_reason[:255]
            db.commit()
    except Exception as db_err:
        db.rollback()
        logger.error(f"Failed to update job {job_id} status to FAILED: {db_err}")
    finally:
        db.close()


@celery_app.task(
    name="tasks.generate_pdf_task",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    soft_time_limit=30,
    time_limit=45
)
def generate_pdf_task(self, job_id: str, payload: dict = None):
    os.makedirs(PDF_STORAGE_DIR, exist_ok=True)
    pdf_filename = f"enterprise_report_{job_id}.pdf"
    pdf_path = os.path.join(PDF_STORAGE_DIR, pdf_filename)

    if not payload:
        payload = {
            "client_name": "Enterprise Client Corp.",
            "client_address": "500 Technology Parkway, Suite 200\nAustin, TX 78701",
            "client_email": "ap@enterprise-client.io",
            "po_number": "PO-2026-8841",
            "items": [{"description": "Async Distributed Compute Allocation", "quantity": 1, "unit_price": 190.00}]
        }

    try:
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )
        story = []
        styles = getSampleStyleSheet()

        COLOR_PRIMARY = colors.HexColor('#0F172A')
        COLOR_ACCENT = colors.HexColor('#2563EB')
        COLOR_TEXT_MAIN = colors.HexColor('#334155')
        COLOR_MUTED = colors.HexColor('#64748B')
        COLOR_BG_LIGHT = colors.HexColor('#F8FAFC')
        COLOR_BORDER = colors.HexColor('#E2E8F0')

        style_comp_info = ParagraphStyle('CompInfo', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=COLOR_MUTED)
        style_inv_meta = ParagraphStyle('InvMeta', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=13, textColor=COLOR_MUTED, alignment=TA_RIGHT)
        style_body = ParagraphStyle('BodyText', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=COLOR_TEXT_MAIN)
        style_body_right = ParagraphStyle('BodyRight', parent=style_body, alignment=TA_RIGHT)
        style_table_hdr = ParagraphStyle('TblHdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=COLOR_PRIMARY)
        style_table_hdr_right = ParagraphStyle('TblHdrRight', parent=style_table_hdr, alignment=TA_RIGHT)

        issue_date = datetime.utcnow()
        due_date = issue_date + timedelta(days=30)

        # Header Section
        left_header = Paragraph(f"""
            <font color='{COLOR_PRIMARY.hexval()}' size=14><b>MICROSTACK SYSTEMS INC.</b></font><br/>
            <font color='{COLOR_MUTED.hexval()}'>
            100 Cloud Native Way, Suite 400<br/>
            San Francisco, CA 94105<br/>
            Tax ID / EIN: 94-3829101<br/>
            billing@microstack.io
            </font>
        """, style_comp_info)

        po_num = payload.get("po_number", "PO-2026-8841")
        short_id = job_id[:8].upper()
        right_header = Paragraph(f"""
            <font color='{COLOR_PRIMARY.hexval()}' size=16><b>INVOICE</b></font><br/><br/>
            <b>Invoice #:</b> INV-{short_id}<br/>
            <b>Issue Date:</b> {issue_date.strftime('%b %d, %Y')}<br/>
            <b>Due Date:</b> {due_date.strftime('%b %d, %Y')} (Net 30)<br/>
            <b>PO Number:</b> {po_num}
        """, style_inv_meta)

        header_table = Table([[left_header, right_header]], colWidths=[300, 240])
        header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER, spaceBefore=4, spaceAfter=14))

        # Billed To Section
        c_name = payload.get("client_name", "Enterprise Client Corp.")
        c_addr = payload.get("client_address", "500 Technology Parkway").replace("\n", "<br/>")
        c_email = payload.get("client_email", "ap@enterprise-client.io")

        billed_to = Paragraph(f"""
            <font color='{COLOR_PRIMARY.hexval()}'><b>BILLED TO</b></font><br/>
            <b>{c_name}</b><br/>
            {c_addr}<br/>
            {c_email}
        """, style_body)

        account_summary = Paragraph(f"""
            <font color='{COLOR_PRIMARY.hexval()}'><b>ACCOUNT & PAYMENT STATUS</b></font><br/>
            <b>Account ID:</b> CUST-99214<br/>
            <b>Payment Terms:</b> Net 30<br/>
            <b>Status:</b> <font color='#16A34A'><b>DUE IN 30 DAYS</b></font>
        """, style_body)

        summary_table = Table([[billed_to, account_summary]], colWidths=[270, 270])
        summary_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 16))

        # Line Items Table
        table_data = [[
            Paragraph("Service Description", style_table_hdr),
            Paragraph("Qty / Hrs", style_table_hdr_right),
            Paragraph("Rate ($)", style_table_hdr_right),
            Paragraph("Amount ($)", style_table_hdr_right)
        ]]

        subtotal = 0.0
        for item in payload.get("items", []):
            desc = item.get("description", "Service")
            qty = item.get("quantity", 1)
            rate = item.get("unit_price", 0.0)
            amount = qty * rate
            subtotal += amount
            table_data.append([
                Paragraph(desc, style_body),
                Paragraph(str(qty), style_body_right),
                Paragraph(f"{rate:,.2f}", style_body_right),
                Paragraph(f"{amount:,.2f}", style_body_right)
            ])

        line_table = Table(table_data, colWidths=[280, 60, 100, 100])
        line_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_BG_LIGHT),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, 0), 1, COLOR_PRIMARY),
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, COLOR_BORDER),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 14))

        # Remittance & Totals
        tax = subtotal * 0.08
        grand_total = subtotal + tax

        remittance = Paragraph(f"""
            <font color='{COLOR_PRIMARY.hexval()}'><b>PAYMENT REMITTANCE INSTRUCTIONS</b></font><br/>
            <font color='{COLOR_MUTED.hexval()}'>
            <b>Bank Name:</b> First Tech Commercial Bank<br/>
            <b>Routing / ABA:</b> 121000358<br/>
            <b>Account Number:</b> 9876543210<br/>
            <b>SWIFT / BIC:</b> FTCBUS33XXX
            </font>
        """, style_body)

        totals_data = [
            [Paragraph("Subtotal:", style_body_right), Paragraph(f"${subtotal:,.2f}", style_body_right)],
            [Paragraph("Estimated Tax (8%):", style_body_right), Paragraph(f"${tax:,.2f}", style_body_right)],
            [
                Paragraph("<b>Total Due:</b>", ParagraphStyle('Ttl', parent=style_body_right, fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_PRIMARY)),
                Paragraph(f"<b>${grand_total:,.2f}</b>", ParagraphStyle('TtlVal', parent=style_body_right, fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_ACCENT))
            ]
        ]
        totals_table = Table(totals_data, colWidths=[120, 100])
        totals_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('LINEABOVE', (0, -1), (-1, -1), 1, COLOR_PRIMARY)
        ]))

        bottom_grid = Table([[remittance, totals_table]], colWidths=[320, 220])
        bottom_grid.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        story.append(bottom_grid)

        story.append(Spacer(1, 24))
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER, spaceBefore=0, spaceAfter=12))

        # Footer
        footer = Paragraph(
            "Thank you for your business! | For billing inquiries, contact <b>billing@microstack.io</b> or call <b>+1 (800) 555-0199</b>.",
            ParagraphStyle('Footer', parent=style_comp_info, alignment=TA_CENTER)
        )
        story.append(footer)

        doc.build(story)

        # DB Completion Update
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "COMPLETED"
                job.result = f"/jobs/{job_id}/download"
                db.commit()
        finally:
            db.close()

        return pdf_path

    except SoftTimeLimitExceeded:
        error_msg = "Task failed: Soft time limit (30s) exceeded."
        logger.error(error_msg)
        _mark_job_failed(job_id, error_msg)

    except Exception as exc:
        logger.warning(f"Task for Job {job_id} encountered exception: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=5)
        else:
            error_msg = f"Task failed after {self.max_retries} retries: {str(exc)}"
            logger.error(error_msg)
            _mark_job_failed(job_id, error_msg)