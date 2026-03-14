import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import AuthContext, require_roles
from api.schemas.requests import AnalyzeExamRequest
from api.schemas.responses import AnalyzeExamAccepted, JobStatusResponse
from data.repository import job_repository
from data.schemas import JobRecord
from pipelines.preprocessing_pipeline import PreprocessingPipeline
from utils.security import emit_audit_event
from workers.tasks import run_analysis

router = APIRouter(prefix="", tags=["analysis"])


@router.post("/analyze_exam", response_model=AnalyzeExamAccepted)
async def analyze_exam(
    payload: AnalyzeExamRequest,
    context: AuthContext = Depends(require_roles(["analyst", "admin"])),
) -> AnalyzeExamAccepted:
    PreprocessingPipeline().validate_inputs(video_path=payload.video_path, audio_path=payload.audio_path)

    job_id = str(uuid.uuid4())
    record = job_repository.create(job_id=job_id)

    try:
        run_analysis.delay(
            job_id=job_id,
            patient_id=payload.patient_id,
            report_text=payload.report_text,
            video_path=payload.video_path,
            audio_path=payload.audio_path,
        )
    except Exception:
        # Keep local/test environment usable without a broker.
        run_analysis(
            job_id=job_id,
            patient_id=payload.patient_id,
            report_text=payload.report_text,
            video_path=payload.video_path,
            audio_path=payload.audio_path,
        )
    emit_audit_event(
        action="analysis_job_created",
        subject_id=job_id,
        actor_id=context.user_id,
        metadata={"patient_id": payload.patient_id, "auth_type": context.auth_type},
    )
    return AnalyzeExamAccepted(job_id=record.job_id, status=record.status)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job(
    job_id: str,
    context: AuthContext = Depends(require_roles(["reviewer", "analyst", "admin"])),
) -> JobStatusResponse:
    record: JobRecord | None = job_repository.get(job_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    emit_audit_event(
        action="analysis_job_accessed",
        subject_id=job_id,
        actor_id=context.user_id,
        metadata={"status": record.status.value, "auth_type": context.auth_type},
    )
    return JobStatusResponse.model_validate(record.model_dump())
