from data.repository import job_repository
from data.schemas import JobStatus
from pipelines.orchestration_pipeline import OrchestrationPipeline
from utils.security import emit_audit_event
from workers.celery_app import celery_app


@celery_app.task(name="workers.tasks.run_analysis")
def run_analysis(job_id: str, patient_id: str, report_text: str, video_path: str, audio_path: str) -> None:
    job_repository.set_status(job_id, JobStatus.processing)
    try:
        pipeline = OrchestrationPipeline()
        result = pipeline.run(
            patient_id=patient_id,
            report_text=report_text,
            video_path=video_path,
            audio_path=audio_path,
        )
        job_repository.set_result(job_id, result.model_dump())
        emit_audit_event(
            action="report_generated",
            subject_id=job_id,
            actor_id="system-worker",
            metadata={"patient_id": patient_id, "discrepancy_count": len(result.discrepancies)},
        )
    except Exception as exc:  # pragma: no cover
        job_repository.set_status(job_id, JobStatus.failed, error=str(exc))
        raise
