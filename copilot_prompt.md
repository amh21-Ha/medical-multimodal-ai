# Production Prompt: Multimodal Medical Exam Analysis System

## Role
You are a senior AI platform engineer and software architect. Build a production-ready Python system that analyzes medical text reports, exam video, and exam audio, then detects and explains discrepancies between documented findings and observed clinical behavior.

## Primary Objective
Deliver a modular, deployable, and testable platform where multiple engineers can work in parallel across NLP, vision, audio, fusion, backend, and MLOps.

## Core Outcomes
1. Extract structured findings from IME text reports.
2. Detect and timestamp exam actions from video.
3. Transcribe and structure clinical audio with speaker segmentation.
4. Fuse all modalities into a single discrepancy engine.
5. Produce explainable reports suitable for legal and clinical review.

## Technology Requirements
- Python 3.11
- PyTorch
- Hugging Face Transformers
- OpenCV
- Whisper (or faster-whisper)
- FastAPI
- PostgreSQL
- Redis
- Celery
- MLflow
- Docker
- Kubernetes-ready deployment manifests

## Non-Functional Requirements
- Reliability: clear retries, timeouts, and failure handling for long-running inference jobs.
- Security: PHI-safe logs, encryption at rest and in transit, RBAC, and auditability.
- Observability: structured logs, metrics, health checks, and traceable job lifecycle.
- Scalability: asynchronous processing for video and audio workloads.
- Reproducibility: pinned dependencies and deterministic experiment tracking.

## Repository Structure
Create and use this structure:

project_root/
|- api/
|  |- main.py
|  |- routers/
|  |  |- analyze.py
|  |- dependencies/
|  |  |- auth.py
|  |- schemas/
|  |  |- requests.py
|  |  |- responses.py
|- pipelines/
|  |- ingestion_pipeline.py
|  |- preprocessing_pipeline.py
|  |- orchestration_pipeline.py
|- models/
|  |- nlp/
|  |  |- medical_report_parser.py
|  |- vision/
|  |  |- exam_action_recognition.py
|  |- audio/
|  |  |- exam_audio_transcriber.py
|  |- fusion/
|  |  |- multimodal_discrepancy_detector.py
|- reporting/
|  |- discrepancy_report_generator.py
|- data/
|  |- schemas.py
|  |- dataset_builder.py
|  |- validation.py
|- mlops/
|  |- experiment_tracking.py
|  |- model_registry.py
|  |- retraining_pipeline.py
|- infrastructure/
|  |- docker/
|  |- kubernetes/
|  |- security/
|- utils/
|  |- config.py
|  |- logging.py
|  |- errors.py
|  |- tracing.py
|- workers/
|  |- celery_app.py
|  |- tasks.py
|- tests/
|  |- unit/
|  |- integration/
|  |- e2e/
|- scripts/
|  |- bootstrap.sh
|  |- run_local.sh
|- pyproject.toml
|- README.md
|- .env.example
|- Dockerfile
|- docker-compose.yml

## Module Specifications

### 1) NLP Module
File: models/nlp/medical_report_parser.py

Implement a transformer-based medical IE pipeline that:
- Ingests unstructured reports.
- Extracts symptoms, exam findings, diagnoses, procedures, and body region.
- Normalizes terms to controlled labels when possible.
- Emits confidence scores and evidence spans.

Output contract example:

{
  "patient_id": "123",
  "symptoms": [{"value": "knee pain", "confidence": 0.94}],
  "exam_findings": [{"value": "limited range of motion", "confidence": 0.91}],
  "diagnoses": [{"value": "ACL injury", "confidence": 0.88}],
  "procedures": [{"value": "left knee Lachman test", "confidence": 0.83}]
}

### 2) Vision Module
File: models/vision/exam_action_recognition.py

Implement exam action recognition that:
- Detects clinically relevant actions and body regions.
- Tracks timestamps and action durations.
- Supports confidence scoring and optional smoothing.
- Handles poor quality video with graceful degradation.

Output contract includes action label, start/end timestamps, body region, and confidence.

### 3) Audio Module
File: models/audio/exam_audio_transcriber.py

Implement audio processing that:
- Performs speech-to-text with Whisper.
- Applies medical term normalization post-processing.
- Performs diarization or pseudo-diarization for clinician/patient turns.
- Emits timestamped transcript segments with confidence.

### 4) Fusion and Discrepancy Detection
File: models/fusion/multimodal_discrepancy_detector.py

Implement a fusion engine that:
- Aligns evidence by timeline and clinical concept.
- Uses embedding similarity plus deterministic rule checks.
- Detects contradiction, omission, and unsupported-claim discrepancy types.
- Assigns severity and confidence per discrepancy.

Example discrepancy:
- Report: Left knee tested.
- Video: No knee exam actions detected.
- Audio: Shoulder-focused discussion.
- Result: contradiction with medium-high confidence.

### 5) Explainable Reporting
File: reporting/discrepancy_report_generator.py

Generate a structured plus narrative report containing:
- discrepancy summary
- itemized evidence (text span, video timestamps, transcript segments)
- confidence and severity
- rationale trace
- reviewer-oriented recommendations

The report must be concise, factual, and non-speculative.

## API Requirements
File: api/main.py

Expose endpoints:
1. POST /analyze_exam
2. GET /jobs/{job_id}
3. GET /health
4. GET /metrics (Prometheus compatible)

Behavior:
- Accept report text and media files.
- Create asynchronous analysis jobs via Celery.
- Return job id immediately.
- Persist outputs and status in PostgreSQL.

## Data and Contracts
- Define strict Pydantic models for every inter-module payload.
- Version payload schemas to prevent breaking changes.
- Validate all inbound and outbound data.

## Security and Compliance
- Encrypt stored artifacts and sensitive fields.
- Redact PHI from logs and tracing payloads.
- Implement RBAC for API access.
- Add audit logs for data access and report generation events.
- Align with HIPAA/GDPR principles (minimum necessary access, retention controls, traceability).

## MLOps Requirements
- Track experiments, params, metrics, and artifacts in MLflow.
- Add model registry integration with stage transitions.
- Support dataset and feature versioning.
- Provide retraining pipeline trigger and evaluation gate.

## Testing Requirements
Implement at minimum:
- Unit tests for NLP extraction, video action parsing, audio transcription post-processing, and fusion logic.
- Integration tests for end-to-end pipeline orchestration.
- API tests for analyze and job status endpoints.
- Failure-path tests for corrupted media, missing data, and timeout/retry behavior.

Target coverage:
- Minimum 80 percent coverage for core business logic modules.

## DevOps and Deployment
- Provide Dockerfile and docker-compose local stack (API, worker, Redis, PostgreSQL, MLflow).
- Add Kubernetes manifests for API, worker, Redis, and PostgreSQL connections.
- Include readiness/liveness probes and resource requests/limits.

## Engineering Standards
- Use typed Python with clear interfaces.
- Keep modules decoupled and testable.
- Use structured logging and custom exception hierarchy.
- Avoid hardcoded paths and secrets.
- Provide clear README with setup, run, test, and deploy instructions.

## Delivery Checklist
The implementation is complete only if all are true:
1. Project boots locally with one command via docker-compose.
2. POST /analyze_exam accepts sample inputs and returns a job id.
3. Job completes and outputs discrepancy report plus structured evidence.
4. Unit and integration tests pass.
5. Security controls (redaction, RBAC hooks, encrypted storage strategy) are present.
6. MLflow tracking and model registration hooks are functional.
7. Kubernetes manifests are valid and deployment-ready.

## Implementation Guidance
Build incrementally in this order:
1. Contracts and schemas.
2. Single-modality baseline modules.
3. Fusion logic.
4. API plus async orchestration.
5. Reporting.
6. Security and MLOps wiring.
7. Tests, hardening, and documentation.

Return clean, modular code that is ready for team-based parallel development and production deployment.
