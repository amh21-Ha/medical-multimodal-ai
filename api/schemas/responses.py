from datetime import datetime
from pydantic import BaseModel

from data.schemas import AnalysisResult, JobStatus


class AnalyzeExamAccepted(BaseModel):
    job_id: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    error: str | None = None
    result: AnalysisResult | None = None
