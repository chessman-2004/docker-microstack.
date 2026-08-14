import os
import pytest
from fastapi.testclient import TestClient
from main import app
from config import settings
from models import Job

client = TestClient(app)

def test_liveness_probe():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_readiness_probe():
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

def test_create_job_unauthorized():
    response = client.post("/jobs/", json={"task_type": "invoice"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing X-API-Key header"

def test_create_job_authorized(mocker):
    mocker.patch("tasks.generate_pdf_task.delay")
    headers = {settings.API_KEY_NAME: settings.API_KEY}
    payload = {
        "task_type": "enterprise_platypus_invoice",
        "client_name": "Test Client Inc."
    }
    
    response = client.post("/jobs/", json=payload, headers=headers)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["status"] == "PENDING"

def test_list_jobs():
    response = client.get("/jobs/")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_job_by_id(mocker):
    mocker.patch("tasks.generate_pdf_task.delay")
    headers = {settings.API_KEY_NAME: settings.API_KEY}
    
    # Create job
    create_res = client.post("/jobs/", json={"task_type": "test"}, headers=headers)
    job_id = create_res.json()["id"]

    # Fetch job
    get_res = client.get(f"/jobs/{job_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == job_id

def test_get_nonexistent_job():
    response = client.get("/jobs/non-existent-uuid-1234")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

def test_download_pdf_not_found():
    headers = {settings.API_KEY_NAME: settings.API_KEY}
    response = client.get("/jobs/fake-id/download", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "PDF asset file missing on disk storage"