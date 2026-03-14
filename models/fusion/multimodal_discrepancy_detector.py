from data.schemas import AudioSegment, Discrepancy, DiscrepancyType, TextFindings, VideoObservation


class MultimodalDiscrepancyDetector:
    """Rule-first discrepancy detector with room for embedding scoring."""

    def detect(
        self,
        text_findings: TextFindings,
        video_observations: list[VideoObservation],
        audio_segments: list[AudioSegment],
    ) -> list[Discrepancy]:
        discrepancies: list[Discrepancy] = []

        report_mentions_knee = any("knee" in proc.value.lower() for proc in text_findings.procedures)
        video_mentions_knee = any("knee" in obs.body_region.lower() for obs in video_observations)
        audio_mentions_shoulder = any("shoulder" in seg.text.lower() for seg in audio_segments)

        if report_mentions_knee and not video_mentions_knee and audio_mentions_shoulder:
            discrepancies.append(
                Discrepancy(
                    discrepancy_type=DiscrepancyType.contradiction,
                    summary="Report indicates a knee exam, but video/audio support shoulder-focused exam.",
                    severity="high",
                    confidence=0.84,
                    supporting_evidence=[
                        "Text: procedure mentions knee exam",
                        "Video: no knee-body-region observations",
                        "Audio: clinician states shoulder exam",
                    ],
                )
            )

        return discrepancies
