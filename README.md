# 🚀 Production-Hardened Asynchronous Microservices Platform

[![Docker CI/CD & DevSecOps Pipeline](https://github.com/YOUR-GITHUB-USERNAME/docker-microstack/actions/workflows/docker-ci.yml/badge.svg)](https://github.com/YOUR-GITHUB-USERNAME/docker-microstack/actions)
![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15--Alpine-4169E1?logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.3.6-37814A?logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7--Alpine-DC382D?logo=redis&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-v2.50.0-E6522C?logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-10.3.3-F46800?logo=grafana&logoColor=white)

An enterprise-ready, containerized 7-service microservice stack featuring an asynchronous task engine, persistent relational storage, zero-downtime dependency orchestration, complete network isolation, and live telemetry observability.

---

## 📐 System Architecture

```text
                               ┌---> [ FastAPI (API Gateway) ] ---\
[ Public ] ---> [ Nginx Proxy ]┤                                  +---> [ PostgreSQL DB ]
  (:8080)          (:80)       └---> [ Celery Worker ] -----------/            ▲
                                             ▲                                 │
                                             └── [ Redis Broker ] ─────────────┘
                                                     ▲
                                         [ Prometheus + Grafana ]
                                          (:9090)        (:3000)

Network Topology & Isolation Boundaries
frontend-net (Bridge): Exposes Nginx (:8080), Prometheus (:9090), and Grafana (:3000) to host traffic.

backend-net (Internal Bridge - internal: true): Connects API, Celery Worker, PostgreSQL, and Redis. This network has zero outbound/inbound public internet exposure.

Service,Technology,Role
Gateway,Nginx (alpine),"Reverse proxy, TLS termination readiness, client header forwarding"
API Server,FastAPI / Uvicorn,RESTful API gateway exposing asynchronous processing triggers
Worker Engine,Celery,Distributed asynchronous task execution engine
Message Broker,Redis 7 (alpine),In-memory message queue and ephemeral metrics counter
Database,PostgreSQL 15 (alpine),Persistent relational database storing background job records
Metrics Collector,Prometheus,Time-series scraper querying FastAPI /metrics telemetry
Visualization,Grafana,"Live graphical dashboards for throughput, latency, and system health"

✨ Enterprise & DevSecOps Features
1. Hardened Security & Multi-Stage Builds
Multi-Stage Dockerfile: Utilizes a builder stage (python:3.11-alpine) to compile C-extensions before discarding compilers (gcc, musl-dev) in the runtime image, cutting final image size by ~85%.

Least Privilege Context: Drops root privileges inside containers to run strictly as an unprivileged user (USER appuser).

Automated Security Scanning: Integrated Hadolint for Dockerfile static linting and Trivy for CVE vulnerability scanning inside CI/CD pipelines.

2. Dependency Orchestration & Dynamic Health Checks
Preventing Startup Race Conditions: The application worker and API use container healthchecks (pg_isready, redis-cli ping) alongside a custom TCP socket check in entrypoint.sh to ensure database readiness prior to execution.

Auto-Schema Ingestion: entrypoint.sh automatically evaluates ORM database models and initializes PostgreSQL tables on boot without manual migration intervention.

3. Asynchronous Distributed Execution
High-latency workloads (e.g., PDF generation, data processing) respond immediately with 202 Accepted and are dispatched to Celery background workers via Redis, keeping HTTP API response latency <50ms.

🚦 Quickstart Guide
Prerequisites
Docker Desktop installed on macOS/Linux/Windows.

git and curl.

1. Clone the Repository
git clone https://github.com/chessman-2004/docker-microstack.git
cd docker-microstack

2. Build & Launch the 7-Container Platform
docker compose up -d --build

3. Verify System Health
Check that all 7 containers are active and healthy:
docker compose ps

🧪 Testing & Verification
Submit a Background Job
Trigger an asynchronous processing task through Nginx:
curl -X POST "http://localhost:8080/jobs/?task_type=financial_statement_pdf"

Response:

{
  "message": "Job queued for background processing",
  "job_id": 1,
  "status": "PENDING"
}

Check Job Processing Status
Query PostgreSQL records via the REST API:
curl "http://localhost:8080/jobs/"
(After 10 seconds, the status will transition automatically from PENDING → COMPLETED).

📊 Observability Dashboards
1. Prometheus Metrics (http://localhost:9090)
Navigate to http://localhost:9090 and run the following PromQL query to view API HTTP throughput telemetry:
http_requests_total

2. Grafana Dashboard (http://localhost:3000)
Access Grafana at http://localhost:3000 (Credentials: admin / admin).

Navigate to Connections > Data Sources > Add Data Source and choose Prometheus.

Set URL to http://prometheus:9090 and click Save & Test.

.

🔒 CI/CD & DevSecOps Pipeline
The included GitHub Actions workflow (.github/workflows/docker-ci.yml) triggers on every push to main and executes:

Hadolint Audit: Lints Dockerfile best practices and formatting.

Trivy CVE Audit: Scans built container images for OS and library vulnerabilities (CRITICAL, HIGH).

Multi-Arch Compilation: Builds images concurrently for linux/amd64 and linux/arm64 architectures via Docker Buildx and QEMU.

📂 Repository Layout

.
├── .github/workflows/
│   └── docker-ci.yml          # DevSecOps CI/CD workflow
├── app/
│   ├── celery_app.py          # Celery worker configuration
│   ├── database.py            # SQLAlchemy database engine setup
│   ├── entrypoint.sh          # Dependency wait & migration script
│   ├── main.py                # FastAPI endpoints & Prometheus exporter
│   ├── models.py              # PostgreSQL database schemas
│   ├── requirements.txt       # Pinned application dependencies
│   └── tasks.py               # Celery asynchronous task definitions
├── nginx/
│   └── default.conf           # Gateway reverse proxy configuration
├── prometheus/
│   └── prometheus.yml         # Prometheus scraping target rules
├── Dockerfile                 # Multi-stage hardened build file
├── docker-compose.yml         # 7-container orchestration topology
└── README.md                  # System documentation