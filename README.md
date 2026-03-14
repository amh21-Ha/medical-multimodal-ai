# Multimodal Medical AI

Production-oriented baseline for multimodal exam discrepancy detection across report text, video, and audio.

## Features
- FastAPI API with async job dispatch through Celery.
- Typed Pydantic contracts for all core payloads.
- Modular NLP, vision, audio, fusion, and reporting layers.
- Real framework-backed inference paths with resilient fallbacks:
   - Transformers NER pipeline for report parsing
   - OpenCV motion-based exam action segmentation
   - Whisper transcription with timestamped segments
- MLflow experiment and model registry hooks.
- Docker Compose stack for local development.
- Kubernetes deployment manifests for API/worker/data services.
- PostgreSQL-backed job repository and Alembic migrations.
- JWT + RBAC auth with optional API-key fallback for bootstrap.

## Quick start
1. Copy environment file:
   cp .env.example .env
2. Build and run:
   docker compose up --build
3. Run migrations (if using postgres backend):
   ./scripts/migrate.sh
3. Open API docs:
   http://localhost:8000/docs

## API
- POST /api/v1/analyze_exam
- GET /api/v1/jobs/{job_id}
- GET /health
- GET /metrics

Use header `x-api-key` with value from `.env`.

For JWT auth, send `Authorization: Bearer <token>` where token claims contain:
- `sub`: user id
- `roles`: list (for example `analyst`, `reviewer`, `admin`)
- `iss`: issuer matching `JWT_ISSUER`
- `aud`: audience matching `JWT_AUDIENCE`

Token helper:
`python scripts/generate_jwt.py --secret "$JWT_SECRET_KEY" --roles analyst`

## Testing
Run:
pytest

## Notes
- Current model components are deterministic placeholders so integration is testable immediately.
- Configure `JOB_REPOSITORY_BACKEND=postgres` for production persistence and multi-worker consistency.
- API routes include audit events with PHI redaction safeguards for metadata fields.
