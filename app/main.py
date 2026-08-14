# import os
# from typing import List, Optional
# from fastapi import FastAPI, HTTPException, Depends, Query
# from fastapi.responses import FileResponse
# from pydantic import BaseModel, Field
# from sqlalchemy.orm import Session

# from database import SessionLocal
# from models import Job
# from tasks import generate_pdf_task, PDF_STORAGE_DIR

# # Note: Schema creation is now handled exclusively via Alembic migrations.

# app = FastAPI(title="Microstack Enterprise API")


# # --- Pydantic Schemas ---
# class LineItem(BaseModel):
#     description: str
#     quantity: int = Field(default=1, ge=1)
#     unit_price: float = Field(default=0.0, ge=0.0)


# class JobCreate(BaseModel):
#     task_type: str = "enterprise_platypus_invoice"
#     client_name: str = "Enterprise Client Corp."
#     client_address: str = "500 Technology Parkway, Suite 200\nAustin, TX 78701"
#     client_email: str = "ap@enterprise-client.io"
#     po_number: str = "PO-2026-8841"
#     items: Optional[List[LineItem]] = Field(default_factory=lambda: [
#         LineItem(description="Async Distributed Compute Cluster Allocation", quantity=1, unit_price=190.00),
#         LineItem(description="PostgreSQL Managed Database Storage Volume (PVC)", quantity=2, unit_price=45.00)
#     ])


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# @app.post("/jobs/")
# def create_job(payload: JobCreate = JobCreate(), db: Session = Depends(get_db)):
#     job = Job(task_type=payload.task_type, status="PENDING")
#     db.add(job)
#     db.commit()
#     db.refresh(job)

#     # Dispatch Celery task passing UUID string job.id
#     generate_pdf_task.delay(job.id, payload.dict())
#     return job


# @app.get("/jobs/")
# def list_jobs(
#     skip: int = Query(0, ge=0, description="Number of records to skip"),
#     limit: int = Query(20, ge=1, le=100, description="Max records to return"),
#     db: Session = Depends(get_db)
# ):
#     jobs = db.query(Job).offset(skip).limit(limit).all()
#     total_count = db.query(Job).count()
#     return {
#         "data": jobs,
#         "pagination": {"skip": skip, "limit": limit, "total": total_count}
#     }


# @app.get("/jobs/{job_id}")
# def get_job(job_id: str, db: Session = Depends(get_db)):
#     job = db.query(Job).filter(Job.id == job_id).first()
#     if not job:
#         raise HTTPException(status_code=404, detail="Job not found")
#     return job


# @app.get("/jobs/{job_id}/download")
# def download_pdf(job_id: str):
#     file_path = os.path.join(PDF_STORAGE_DIR, f"enterprise_report_{job_id}.pdf")

#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="PDF asset file missing on disk storage")

#     return FileResponse(
#         path=file_path,
#         filename=f"invoice_{job_id}.pdf",
#         media_type="application/pdf"
#     )
import os
import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query, Request, Response, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

from config import settings
from database import SessionLocal
from models import Job
from tasks import generate_pdf_task
from auth import verify_api_key
from logger import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Database Dependency (Defined FIRST) ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Middleware for Request Correlation IDs & Structured Logs ---
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    
    logger.info(
        f"Incoming request {request.method} {request.url.path}",
        extra={"request_id": request_id, "method": request.method, "path": request.url.path}
    )
    
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# --- Kubernetes Liveness & Readiness Health Probes ---
@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["Probes"])
def liveness_probe():
    """Liveness probe to confirm app process is running."""
    return {"status": "healthy"}

@app.get("/readyz", status_code=status.HTTP_200_OK, tags=["Probes"])
def readiness_probe(db: Session = Depends(get_db)):
    """Readiness probe to confirm DB connectivity before routing traffic."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection unready")

# --- Schemas ---
class LineItem(BaseModel):
    description: str
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(default=0.0, ge=0.0)

class JobCreate(BaseModel):
    task_type: str = "enterprise_platypus_invoice"
    client_name: str = "Enterprise Client Corp."
    client_address: str = "500 Technology Parkway, Suite 200\nAustin, TX 78701"
    client_email: str = "ap@enterprise-client.io"
    po_number: str = "PO-2026-8841"
    items: Optional[List[LineItem]] = Field(default_factory=lambda: [
        LineItem(description="Async Distributed Compute Cluster Allocation", quantity=1, unit_price=190.00),
        LineItem(description="PostgreSQL Managed Database Storage Volume (PVC)", quantity=2, unit_price=45.00)
    ])

# --- Protected Application Endpoints ---
@app.post("/jobs/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_api_key)])
def create_job(
    request: Request,
    payload: JobCreate = JobCreate(),
    db: Session = Depends(get_db)
):
    job = Job(task_type=payload.task_type, status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)

    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    generate_pdf_task.delay(job.id, payload.model_dump(), request_id)
    
    logger.info(f"Dispatched PDF job {job.id}", extra={"request_id": request_id, "job_id": job.id})
    return job

@app.get("/jobs/")
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).offset(skip).limit(limit).all()
    total_count = db.query(Job).count()
    return {
        "data": jobs,
        "pagination": {"skip": skip, "limit": limit, "total": total_count}
    }

@app.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/jobs/{job_id}/download", dependencies=[Depends(verify_api_key)])
def download_pdf(job_id: str):
    file_path = os.path.join(settings.PDF_STORAGE_DIR, f"enterprise_report_{job_id}.pdf")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF asset file missing on disk storage")

    return FileResponse(
        path=file_path,
        filename=f"invoice_{job_id}.pdf",
        media_type="application/pdf"
    )