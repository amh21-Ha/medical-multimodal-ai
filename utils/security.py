from __future__ import annotations

import logging
import re
from typing import Any


LOGGER = logging.getLogger("audit")

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,2}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
DOB_RE = re.compile(r"\b(?:DOB|Date of Birth)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", re.IGNORECASE)


def redact_phi(text: str) -> str:
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    redacted = PHONE_RE.sub("[REDACTED_PHONE]", redacted)
    redacted = SSN_RE.sub("[REDACTED_SSN]", redacted)
    redacted = DOB_RE.sub("[REDACTED_DOB]", redacted)
    return redacted


def _redact_obj(value: Any) -> Any:
    if isinstance(value, str):
        return redact_phi(value)
    if isinstance(value, list):
        return [_redact_obj(v) for v in value]
    if isinstance(value, dict):
        return {k: _redact_obj(v) for k, v in value.items()}
    return value


def redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return _redact_obj(payload)


def emit_audit_event(action: str, subject_id: str, actor_id: str, metadata: dict[str, Any] | None = None) -> None:
    LOGGER.info(
        "audit_event",
        extra={
            "action": action,
            "subject_id": subject_id,
            "actor_id": actor_id,
            "metadata": redact_payload(metadata or {}),
        },
    )
