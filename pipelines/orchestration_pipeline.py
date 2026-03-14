from data.schemas import AnalysisResult
from models.audio.exam_audio_transcriber import ExamAudioTranscriber
from models.fusion.multimodal_discrepancy_detector import MultimodalDiscrepancyDetector
from models.nlp.medical_report_parser import MedicalReportParser
from models.vision.exam_action_recognition import ExamActionRecognizer
from reporting.discrepancy_report_generator import DiscrepancyReportGenerator


class OrchestrationPipeline:
    def __init__(self) -> None:
        self.parser = MedicalReportParser()
        self.vision = ExamActionRecognizer()
        self.audio = ExamAudioTranscriber()
        self.fusion = MultimodalDiscrepancyDetector()
        self.reporter = DiscrepancyReportGenerator()

    def run(self, patient_id: str, report_text: str, video_path: str, audio_path: str) -> AnalysisResult:
        text_findings = self.parser.parse(patient_id=patient_id, report_text=report_text)
        video_observations = self.vision.infer(video_path=video_path)
        audio_segments = self.audio.transcribe(audio_path=audio_path)
        discrepancies = self.fusion.detect(
            text_findings=text_findings,
            video_observations=video_observations,
            audio_segments=audio_segments,
        )

        result = AnalysisResult(
            text_findings=text_findings,
            video_observations=video_observations,
            audio_segments=audio_segments,
            discrepancies=discrepancies,
            narrative_report="",
        )
        result.narrative_report = self.reporter.render(result)
        return result
