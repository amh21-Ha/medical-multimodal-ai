from pathlib import Path

from pipelines.orchestration_pipeline import OrchestrationPipeline


def test_orchestration_pipeline_returns_report(tmp_path: Path) -> None:
    video = tmp_path / "exam.mp4"
    audio = tmp_path / "exam.wav"
    video.write_bytes(b"fake-video")
    audio.write_bytes(b"fake-audio")

    pipeline = OrchestrationPipeline()
    result = pipeline.run(
        patient_id="p1",
        report_text="Left knee tested. Knee pain reported.",
        video_path=str(video),
        audio_path=str(audio),
    )

    assert result.narrative_report
    assert result.text_findings.patient_id == "p1"
