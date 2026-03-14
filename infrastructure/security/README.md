# Security Baseline

This folder documents baseline controls for handling protected medical data.

## Required controls
- Enforce TLS termination at ingress.
- Use encrypted storage for media artifacts.
- Store secrets in a secure secret manager.
- Redact PHI from logs and telemetry payloads.
- Enable per-request audit records for data access and report generation.

## RBAC recommendation
- Role `reviewer`: view analysis and reports.
- Role `analyst`: submit exams and view own jobs.
- Role `admin`: manage system settings and model versions.
