# 🚀 Production-Hardened Asynchronous Microservices Platform

[![Docker CI/CD & DevSecOps Pipeline](https://img.shields.io/github/actions/workflow/status/chessman-2004/docker-microstack/docker-ci.yml?branch=main&label=Docker%20CI%2FCD%20%26%20DevSecOps%20Pipeline&status=passed)](https://github.com/chessman-2004/docker-microstack/actions/workflows/docker-ci.yml)
![Kubernetes](https://img.shields.io/badge/Kubernetes-v1.28+-326CE5?logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15--Alpine-4169E1?logo=postgresql&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-6A1B9A?logo=python&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.3.6-37814A?logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7--Alpine-DC382D?logo=redis&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-v2.50.0-E6522C?logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-10.3.3-F46800?logo=grafana&logoColor=white)

An enterprise-ready, containerized microservice stack featuring an asynchronous PDF generation engine, versioned database schema migrations, complete Kubernetes orchestration, persistent shared volume storage, zero-downtime dependency management, and live telemetry observability.

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

| Service | Technology | Role |
| :--- | :--- | :--- |
| **Gateway** | Nginx (alpine) | Reverse proxy, TLS termination readiness, client header forwarding |
| **API Server** | FastAPI / Uvicorn | RESTful API gateway exposing asynchronous processing triggers & PDF streams |
| **Worker Engine** | Celery | Distributed asynchronous task execution engine for PDF generation |
| **Message Broker** | Redis 7 (alpine) | In-memory message queue and ephemeral task state broker |
| **Database** | PostgreSQL 15 (alpine) | Persistent relational database storing job records (StatefulSet) |
| **Migrations** | Alembic | Version-controlled database schema evolution scripts |
| **Shared Storage** | Docker Volume / PVC | Shared file storage mount (`/app/generated_pdfs`) for binary PDF assets |
| **Metrics Collector** | Prometheus | Time-series scraper querying FastAPI `/metrics` telemetry |
| **Visualization** | Grafana | Live graphical dashboards for throughput, latency, and system health |

✨ Enterprise & DevSecOps Features
1. Hardened Security & Multi-Stage Builds
Multi-Stage Dockerfile: Utilizes a builder stage (python:3.11-alpine) to compile C-extensions before discarding compilers (gcc, musl-dev) in the runtime image, cutting final image size by ~85%.

Least Privilege Context: Drops root privileges inside containers to run strictly as an unprivileged user (USER appuser).

Automated Security Scanning: Integrated Hadolint for Dockerfile static linting and Trivy for CVE vulnerability scanning inside CI/CD pipelines.

2. Production Database Migrations & Schema Control
Alembic Versioning: Replaced static table initialization (create_all()) with Alembic version-controlled migration scripts, allowing safe schema upgrades and rollbacks in production environments.

Dependency Orchestration: Uses container healthchecks (pg_isready, redis-cli ping) and startup scripts to guarantee database readiness prior to execution.

3. Asynchronous PDF Generation Engine
ReportLab Processing Pipeline: High-latency document processing is dispatched to Celery background workers via Redis. Workers render PDF reports using ReportLab and write directly to a shared volume (/app/generated_pdfs).

Binary File Streaming: FastAPI streams generated PDF binaries directly to client browsers via dedicated /jobs/{job_id}/download endpoints.

4. Cloud-Native Kubernetes Orchestration
Complete Manifest Suite (/k8s): Includes Kubernetes manifests for Deployments (API, Worker, Cache), StatefulSets (PostgreSQL), PersistentVolumeClaims (Shared PDF storage), Services, ConfigMaps, and Secrets.

Resiliency & Self-Healing: Configured with readiness/liveness HTTP probes to support zero-downtime rolling deployment updates.

🚦 Quickstart Guide
Prerequisites
Docker Desktop installed on macOS/Linux/Windows (with Kubernetes enabled for K8s deployment).

git, curl, and kubectl (optional).

1. Clone the Repository

git clone [https://github.com/chessman-2004/docker-microstack.git](https://github.com/chessman-2004/docker-microstack.git)
cd docker-microstack

2. Option A: Launch via Docker Compose

# Build and launch all 7 containers
docker compose up -d --build

# Apply database migrations
docker compose exec api alembic upgrade head

3. Option B: Deploy to Kubernetes Cluster

# 1. Build local container image
docker build -t docker-microstack-app:latest .

# 2. Deploy all manifests to Kubernetes
kubectl apply -f k8s/

# 3. Verify pod status
kubectl get pods

# 4. Access API via port-forwarding
kubectl port-forward service/api 8000:8000

🧪 Testing & Verification
1. Submit an Asynchronous PDF Task
Trigger a background PDF compilation job through the API gateway:

curl -X POST "http://localhost:8080/jobs/?task_type=phase2_alembic_pdf"

Response:

{
  "message": "PDF generation task dispatched to Celery worker",
  "job_id": 1,
  "status": "PENDING"
}

2. Check Job Processing Status
Query PostgreSQL records via the REST API:

curl "http://localhost:8080/jobs/"

When completed, the response will show the download link:

{
  "total_jobs_queued": "1",
  "jobs": [
    {
      "id": 1,
      "task_type": "phase2_alembic_pdf",
      "status": "COMPLETED",
      "result": "/jobs/1/download",
      "created_at": "2026-08-09T18:00:00"
    }
  ]
}

3. Stream & Download Generated PDF
Open http://localhost:8080/jobs/1/download directly in your browser or run:

curl -O http://localhost:8080/jobs/1/download

📊 Observability Dashboards
1. Prometheus Metrics (http://localhost:9090)
Navigate to http://localhost:9090 and run the following PromQL query to view API HTTP throughput telemetry:

http_requests_total

2. Grafana Dashboard (http://localhost:3000)
Access Grafana at http://localhost:3000 (Credentials: admin / admin).

Navigate to Connections > Data Sources > Add Data Source and choose Prometheus.

Set URL to http://prometheus:9090 and click Save & Test.

🔒 CI/CD & DevSecOps Pipeline
The included GitHub Actions workflow (.github/workflows/docker-ci.yml) triggers on every push to main and executes:

Hadolint Audit: Lints Dockerfile best practices and formatting.

Trivy CVE Audit: Scans built container images for OS and library vulnerabilities (CRITICAL, HIGH).

Multi-Arch Compilation: Builds images concurrently for linux/amd64 and linux/arm64 architectures via Docker Buildx and QEMU.

📂 Repository Layout

.
├── .github/
│   └── workflows/
│       └── docker-ci.yml      # DevSecOps CI/CD workflow
├── alembic/                    # Database migration scripts & history
│   ├── versions/              # Revision scripts
│   └── env.py                 # Alembic environment configuration
├── app/
│   ├── celery_app.py          # Celery worker configuration
│   ├── database.py            # SQLAlchemy database engine setup
│   ├── entrypoint.sh          # Dependency wait script
│   ├── main.py                # FastAPI endpoints & PDF download router
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
├── alembic.ini                # Alembic database migration settings
├── Dockerfile                 # Multi-stage hardened build file
├── docker-compose.yml         # 7-container orchestration topology
└── README.md                  # System documentation