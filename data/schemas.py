from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class EvidenceItem(BaseModel):
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    start_time_sec: float | None = Field(default=None, ge=0.0)
    end_time_sec: float | None = Field(default=None, ge=0.0)
    body_region: str | None = None


class TextFindings(BaseModel):
    patient_id: str
    symptoms: list[EvidenceItem] = Field(default_factory=list)
    exam_findings: list[EvidenceItem] = Field(default_factory=list)
    diagnoses: list[EvidenceItem] = Field(default_factory=list)
    procedures: list[EvidenceItem] = Field(default_factory=list)


class VideoObservation(BaseModel):
    action: str
    body_region: str
    start_time_sec: float = Field(ge=0.0)
    end_time_sec: float = Field(ge=0.0)
    confidence: float = Field(ge=0.0, le=1.0)


class AudioSegment(BaseModel):
    speaker: str
    text: str
    start_time_sec: float = Field(ge=0.0)
    end_time_sec: float = Field(ge=0.0)
    confidence: float = Field(ge=0.0, le=1.0)


class DiscrepancyType(str, Enum):
    contradiction = "contradiction"
    omission = "omission"
    unsupported_claim = "unsupported_claim"


class Discrepancy(BaseModel):
    discrepancy_type: DiscrepancyType
    summary: str
    severity: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    text_findings: TextFindings
    video_observations: list[VideoObservation]
    audio_segments: list[AudioSegment]
    discrepancies: list[Discrepancy]
    narrative_report: str


class JobRecord(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    error: str | None = None
    result: AnalysisResult | None = None
