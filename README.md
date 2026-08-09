# 🛡️ Production-Hardened Containerized Micro-Stack

![Docker CI/CD Pipeline](https://github.com/chessman-2004/docker-microstack/actions/workflows/docker-ci.yml/badge.svg?branch=main)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat&logo=nginx&logoColor=white)

An enterprise-ready microservices stack featuring an Nginx reverse proxy, FastAPI backend, and Redis cache. Built with strict security hardening, multi-stage optimization, network isolation, and fully automated DevSecOps CI/CD pipelines.

---

## 🏗️ System Architecture

```text
               [ Public Internet ]
                        │
                        ▼ (Port 80)
             ┌─────────────────────┐
             │     Nginx Proxy     │ (frontend-net)
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │    FastAPI Server   │ (frontend-net + backend-net)
             └──────────┬──────────┘
                        │
                        ▼ (Isolated Internal Bridge)
             ┌─────────────────────┐
             │     Redis Cache     │ (backend-net - internal)
             └─────────────────────┘

---
✨ Enterprise & Hardening Features
⚡ Multi-Stage Builds: Utilizes two-stage compilation on Alpine Linux base images to decouple build tools from the runtime environment.

🔒 Security Hardened (Non-Root): Runs container instances under a dedicated, unprivileged non-root user (appuser).

🌐 Isolated Network Topologies: Employs Docker bridge networks (frontend-net, backend-net) with internal restrictions to isolate Redis from public exposure.

🏥 Service-Aware Orchestration: Uses native health checks (redis-cli ping) alongside service_healthy conditions to prevent race conditions.

🛡️ DevSecOps CI/CD Pipeline: Automated GitHub Actions pipeline executing Hadolint linting, Trivy vulnerability scanning, and multi-arch builds (amd64/arm64) with Docker Buildx.