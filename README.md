# 🚀 Production-Hardened Asynchronous Microservices Platform

[![Docker CI/CD & DevSecOps Pipeline](https://github.com/chessman-2004/docker-microstack./actions/workflows/docker-ci.yml/badge.svg)](https://github.com/chessman-2004/docker-microstack./actions/workflows/docker-ci.yml)
![Kubernetes](https://img.shields.io/badge/Kubernetes-v1.28+-326CE5?logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-3776AB?logo=python&logoColor=white)
![Pytest Coverage](https://img.shields.io/badge/Coverage-87%25-brightgreen?logo=pytest&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15--Alpine-4169E1?logo=postgresql&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-6A1B9A?logo=python&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.3.6-37814A?logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7--Alpine-DC382D?logo=redis&logoColor=white)

An enterprise-ready, containerized microservice stack featuring an asynchronous PDF generation engine, API key authentication, distributed request tracing, versioned database schema migrations, complete Kubernetes orchestration, persistent shared volume storage, live telemetry observability, and an isolated unit testing suite achieving **87% code coverage**.

---

## 📐 System Architecture

```text
                               ┌---> [ FastAPI (API Gateway) ] ---\
[ Public ] ---> [ Nginx Proxy ]┤                                  +---> [ PostgreSQL DB (StatefulSet) ]
  (:8080)          (:80)       └---> [ Celery Worker ] -----------/            ▲
                                             │                                 │
                                             ├---> [ Redis Broker ] ───────────┘
                                             │
                                             ├---> [ Shared PDF Storage (PVC) ]
                                             │
                                         [ Prometheus + Grafana ]
                                          (:9090)        (:3000)

Network Topology & Isolation Boundaries
frontend-net (Bridge): Exposes Nginx (:8080), Prometheus (:9090), and Grafana (:3000) to host traffic.

backend-net (Internal Bridge): Connects API, Celery Worker, PostgreSQL, and Redis with zero outbound/inbound public internet exposure.

✨ Enterprise & DevSecOps Features
1. Hardened Security, Auth & Multi-Stage Builds
API Key Header Security: Protected endpoints require a valid X-API-Key header, returning 401 Unauthorized for unauthenticated requests.

Multi-Stage Dockerfile: Utilizes a builder stage (python:3.11-alpine) to compile C-extensions before discarding compilers (gcc, musl-dev) in the runtime image, cutting final image size by ~85%.

Least Privilege Context: Drops root privileges inside containers to run strictly as an unprivileged user (USER appuser).

Automated Security Scanning: Integrated Hadolint for Dockerfile static linting and Trivy for CVE vulnerability scanning inside CI/CD pipelines.

2. Observability, Logging & Tracing
Correlation ID Middleware: Injects or propagates a unique X-Request-ID across HTTP requests and dispatches it through Celery tasks for end-to-end request tracing.

Structured JSON Logging: Implements python-json-logger for standardized JSON logs formatted for ELK/Loki log aggregation.

3. Production Database Migrations & Schema Control
Alembic Versioning: Replaced static table initialization (create_all()) with Alembic version-controlled migration scripts, allowing safe schema upgrades and rollbacks in production environments.

Dependency Orchestration: Uses container healthchecks (pg_isready, redis-cli ping) and startup scripts to guarantee database readiness prior to execution.

4. Asynchronous PDF Generation Engine
ReportLab Processing Pipeline: High-latency document processing is dispatched to Celery background workers via Redis. Workers render PDF reports using ReportLab and write directly to a shared volume (/app/generated_pdfs).

Binary File Streaming: FastAPI streams generated PDF binaries directly to client browsers via dedicated /jobs/{job_id}/download endpoints.

5. Cloud-Native Kubernetes Orchestration
Complete Manifest Suite (/k8s): Includes Kubernetes manifests for Deployments (API, Worker, Cache), StatefulSets (PostgreSQL), PersistentVolumeClaims (Shared PDF storage), Services, ConfigMaps, and Secrets.

Resiliency & Probes: Configured with Liveness (/healthz) and Readiness (/readyz) HTTP health probes for zero-downtime rolling deployment updates.

6. Automated Testing & In-Memory Isolation (87% Coverage)
Isolated Pytest Suite: Uses an in-memory SQLite database (sqlite:///:memory:) and fixture dependency overrides to run unit/integration tests without requiring live PostgreSQL/Redis containers.

Sub-Second Execution: Runs the full test suite in <0.2 seconds while validating route handlers, database persistence, authentication, and PDF generation logic.

🚦 Quickstart Guide
Prerequisites
Docker Desktop installed on macOS/Linux/Windows (with Kubernetes enabled for K8s deployment).

git, curl, and kubectl (optional).

1. Clone the Repository

git clone [https://github.com/chessman-2004/docker-microstack.git](https://github.com/chessman-2004/docker-microstack.git)
cd docker-microstack

2. Launch via Docker Compose

# Build and launch all 7 containers
docker compose up -d --build

# Apply database migrations
docker compose exec api alembic upgrade head

3. Deploy to Kubernetes Cluster

# 1. Build local container image
docker build -t docker-microstack-app:v16 .

# 2. Deploy all manifests to Kubernetes
kubectl apply -f k8s/

# 3. Verify pod status
kubectl get pods

# 4. Access API via port-forwarding
kubectl port-forward service/api 8000:8000

🧪 Testing & Verification
1. Run Automated Pytest Suite Locally
Run the isolated unit test suite with code coverage breakdown:

pytest --cov=app --cov-report=term-missing

Coverage Breakdown:

Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
app/auth.py             8      0   100%
app/celery_app.py       6      6     0%   1-15
app/config.py          12      0   100%
app/database.py        12      4    67%   16-20
app/logger.py          17      3    82%   7-8, 21
app/main.py            77      8    90%   114-118, 147-149, 213
app/models.py          11      0   100%
app/tasks.py          117     14    88%   29-31, 232-244
-------------------------------------------------
TOTAL                 260     35    87%


2. Manual API Endpoint Verification
A. Health Probes

# Liveness Probe
curl http://localhost:8080/healthz

# Readiness Probe (verifies database connectivity)
curl http://localhost:8080/readyz

B. Submit an Authenticated Asynchronous Task

curl -i -X POST http://localhost:8080/jobs/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: microstack-dev-secret-key-change-in-prod" \
  -d '{"task_type": "enterprise_platypus_invoice"}'

Response (HTTP/1.1 201 Created):

{
  "id": "1907a7c0-c2e8-4fbf-9da7-040343c5c74e",
  "status": "PENDING",
  "result": null,
  "task_type": "enterprise_platypus_invoice",
  "created_at": "2026-08-14T16:20:17.486300+00:00"
}

C. Query Job Status

curl "http://localhost:8080/jobs/"

D. Download Generated PDF Report

curl -i http://localhost:8080/jobs/{job_id}/download \
  -H "X-API-Key: microstack-dev-secret-key-change-in-prod" \
  --output invoice.pdf

📊 Observability Dashboards
1. Prometheus Metrics (http://localhost:9090)
Navigate to http://localhost:9090 and run the following PromQL query to view API HTTP throughput telemetry:

http_requests_total

2. Grafana Dashboard (http://localhost:3000)
Access Grafana at http://localhost:3000 (Credentials: admin / admin).

Navigate to Connections > Data Sources > Add Data Source and choose Prometheus.

Set URL to http://prometheus:9090 and click Save & Test.

🔒 CI/CD & DevSecOps Pipeline
The GitHub Actions workflow (.github/workflows/docker-ci.yml) enforces quality gate checks on every push to main across 4 concurrent and sequential jobs:

┌──────────┐
       │   test   │──────┐
       └──────────┘      │
                         ▼
                   ┌──────────────┐      ┌────────────────┐
                   │security-scan │ ───► │ build-and-push │
                   └──────────────┘      └────────────────┘
                         ▲
       ┌──────────┐      │
       │   lint   │──────┘
       └──────────┘


Pytest Unit Tests & Coverage: Runs the full Pytest suite in an isolated Python 3.13 container and uploads coverage.xml.

Hadolint Audit: Lints Dockerfile best practices and formatting.

Trivy CVE Audit: Scans built container images for OS and library vulnerabilities (CRITICAL, HIGH).

Multi-Arch Compilation: Builds images concurrently for linux/amd64 and linux/arm64 architectures via Docker Buildx and QEMU.

📂 Repository Layout

.
├── .github/
│   └── workflows/
│       └── docker-ci.yml      # 4-stage DevSecOps CI/CD workflow
├── alembic/                    # Database migration scripts & history
│   ├── versions/              # Revision scripts
│   └── env.py                 # Alembic environment configuration
├── app/
│   ├── auth.py                # X-API-Key authentication dependency
│   ├── celery_app.py          # Celery worker configuration
│   ├── config.py              # Pydantic v2 application settings
│   ├── database.py            # SQLAlchemy database engine setup
│   ├── entrypoint.sh          # Dependency wait script
│   ├── logger.py              # Structured JSON logging configuration
│   ├── main.py                # FastAPI endpoints, probes & middleware
│   ├── models.py              # PostgreSQL database schemas
│   ├── requirements.txt       # Pinned application dependencies
│   └── tasks.py               # Celery async PDF task worker definitions
├── k8s/                        # Production Kubernetes Manifests
│   ├── api.yaml               # FastAPI deployment & service
│   ├── config.yaml            # ConfigMaps & Secrets
│   ├── postgres.yaml          # PostgreSQL StatefulSet & service
│   ├── pvc.yaml               # Shared Persistent Volume Claim
│   ├── redis.yaml             # Redis broker deployment & service
│   └── worker.yaml            # Celery worker deployment
├── nginx/
│   └── default.conf           # Gateway reverse proxy configuration
├── prometheus/
│   └── prometheus.yml         # Prometheus scraping target rules
├── tests/                      # Automated Test Suite
│   ├── conftest.py            # In-memory SQLite fixtures & session mocks
│   ├── test_api.py            # FastAPI route & auth integration tests
│   └── test_tasks.py          # Celery worker PDF task unit tests
├── alembic.ini                # Alembic database migration settings
├── Dockerfile                 # Multi-stage hardened build file
├── docker-compose.yml         # 7-container orchestration topology
├── pytest.ini                 # Pytest paths and runtime settings
└── README.md                  # System documentation