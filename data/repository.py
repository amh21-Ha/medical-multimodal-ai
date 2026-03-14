from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from threading import Lock

from sqlalchemy import select

from data.schemas import AnalysisResult, JobRecord, JobStatus
from utils.config import get_settings


class JobRepository(ABC):
    @abstractmethod
    def create(self, job_id: str) -> JobRecord:
        raise NotImplementedError

    @abstractmethod
    def get(self, job_id: str) -> JobRecord | None:
        raise NotImplementedError

    @abstractmethod
    def set_status(self, job_id: str, status: JobStatus, error: str | None = None) -> JobRecord | None:
        raise NotImplementedError

    @abstractmethod
    def set_result(self, job_id: str, result_json: dict) -> JobRecord | None:
        raise NotImplementedError


class InMemoryJobRepository(JobRepository):
    def __init__(self) -> None:
        self._lock = Lock()
        self._items: dict[str, JobRecord] = {}

    def create(self, job_id: str) -> JobRecord:
        now = datetime.now(timezone.utc)
        record = JobRecord(job_id=job_id, status=JobStatus.queued, created_at=now, updated_at=now)
        with self._lock:
            self._items[job_id] = record
        return record

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._items.get(job_id)

    def set_status(self, job_id: str, status: JobStatus, error: str | None = None) -> JobRecord | None:
        with self._lock:
            record = self._items.get(job_id)
            if record is None:
                return None
            record.status = status
            record.error = error
            record.updated_at = datetime.now(timezone.utc)
            self._items[job_id] = record
            return record

    def set_result(self, job_id: str, result_json: dict) -> JobRecord | None:
        with self._lock:
            record = self._items.get(job_id)
            if record is None:
                return None
            record.result = AnalysisResult.model_validate(result_json)
            record.status = JobStatus.completed
            record.updated_at = datetime.now(timezone.utc)
            self._items[job_id] = record
            return record


class PostgresJobRepository(JobRepository):
    def create(self, job_id: str) -> JobRecord:
        from data.db import get_session
        from data.db_models import JobORM

        now = datetime.now(timezone.utc)
        with get_session() as session:
            session.add(
                JobORM(
                    job_id=job_id,
                    status=JobStatus.queued.value,
                    created_at=now,
                    updated_at=now,
                )
            )
            session.commit()
        return JobRecord(job_id=job_id, status=JobStatus.queued, created_at=now, updated_at=now)

    def get(self, job_id: str) -> JobRecord | None:
        from data.db import get_session
        from data.db_models import JobORM

        with get_session() as session:
            row = session.scalar(select(JobORM).where(JobORM.job_id == job_id))
            if row is None:
                return None
            result = AnalysisResult.model_validate(row.result_json) if row.result_json else None
            return JobRecord(
                job_id=row.job_id,
                status=JobStatus(row.status),
                created_at=row.created_at,
                updated_at=row.updated_at,
                error=row.error,
                result=result,
            )

    def set_status(self, job_id: str, status: JobStatus, error: str | None = None) -> JobRecord | None:
        from data.db import get_session
        from data.db_models import JobORM

        now = datetime.now(timezone.utc)
        with get_session() as session:
            row = session.scalar(select(JobORM).where(JobORM.job_id == job_id))
            if row is None:
                return None
            row.status = status.value
            row.error = error
            row.updated_at = now
            session.commit()
            return JobRecord(
                job_id=row.job_id,
                status=JobStatus(row.status),
                created_at=row.created_at,
                updated_at=row.updated_at,
                error=row.error,
                result=AnalysisResult.model_validate(row.result_json) if row.result_json else None,
            )

    def set_result(self, job_id: str, result_json: dict) -> JobRecord | None:
        from data.db import get_session
        from data.db_models import JobORM

        now = datetime.now(timezone.utc)
        result = AnalysisResult.model_validate(result_json)
        with get_session() as session:
            row = session.scalar(select(JobORM).where(JobORM.job_id == job_id))
            if row is None:
                return None
            row.result_json = result.model_dump()
            row.status = JobStatus.completed.value
            row.error = None
            row.updated_at = now
            session.commit()
            return JobRecord(
                job_id=row.job_id,
                status=JobStatus(row.status),
                created_at=row.created_at,
                updated_at=row.updated_at,
                error=row.error,
                result=result,
            )


def create_repository() -> JobRepository:
    settings = get_settings()
    if settings.job_repository_backend.lower() == "postgres":
        # Ensure schema exists when using DB-backed repository.
        from data.db import engine
        from data.db_models import Base

        Base.metadata.create_all(bind=engine)
        return PostgresJobRepository()
    return InMemoryJobRepository()


job_repository = create_repository()
