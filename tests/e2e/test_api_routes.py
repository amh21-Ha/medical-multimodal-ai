from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from utils.config import get_settings


client = TestClient(app)


def test_analyze_and_get_job(tmp_path: Path) -> None:
    settings = get_settings()
    video = tmp_path / "exam.mp4"
    audio = tmp_path / "exam.wav"
    video.write_bytes(b"fake-video")
    audio.write_bytes(b"fake-audio")

    payload = {
        "patient_id": "p1",
        "report_text": "Left knee tested",
        "video_path": str(video),
        "audio_path": str(audio),
    }

    res = client.post(
        f"{settings.api_prefix}/analyze_exam",
        json=payload,
        headers={"x-api-key": settings.api_key},
    )

    assert res.status_code == 200
    body = res.json()
    assert body["job_id"]

    status_res = client.get(
        f"{settings.api_prefix}/jobs/{body['job_id']}",
        headers={"x-api-key": settings.api_key},
    )
    assert status_res.status_code == 200
