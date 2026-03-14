from data.schemas import AudioSegment, EvidenceItem, TextFindings, VideoObservation
from models.fusion.multimodal_discrepancy_detector import MultimodalDiscrepancyDetector


def test_fusion_detects_contradiction() -> None:
    detector = MultimodalDiscrepancyDetector()
    text_findings = TextFindings(
        patient_id="p1",
        procedures=[EvidenceItem(value="left knee exam", confidence=0.9)],
    )
    video_observations = [
        VideoObservation(
            action="shoulder_exam",
            body_region="left shoulder",
            start_time_sec=1,
            end_time_sec=4,
            confidence=0.8,
        )
    ]
    audio_segments = [
        AudioSegment(
            speaker="clinician",
            text="Let's check your shoulder",
            start_time_sec=1,
            end_time_sec=2,
            confidence=0.9,
        )
    ]

    discrepancies = detector.detect(text_findings, video_observations, audio_segments)
    assert discrepancies
    assert discrepancies[0].summary
