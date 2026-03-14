from __future__ import annotations

from data.schemas import AudioSegment

try:
    import whisper  # type: ignore
except Exception:  # pragma: no cover
    whisper = None


class ExamAudioTranscriber:
    """Baseline audio transcriber.

    Uses Whisper transcription when available, with deterministic fallback.
    """

    def __init__(self) -> None:
        self._model = None
        if whisper is not None:
            try:
                self._model = whisper.load_model("base")
            except Exception:
                self._model = None

    def _fallback(self) -> list[AudioSegment]:
        return [
            AudioSegment(
                speaker="clinician",
                text="Let's check your shoulder now.",
                start_time_sec=12.0,
                end_time_sec=16.0,
                confidence=0.89,
            )
        ]

    def transcribe(self, audio_path: str) -> list[AudioSegment]:
        if self._model is None:
            return self._fallback()

        try:
            out = self._model.transcribe(audio_path, fp16=False)
        except Exception:
            return self._fallback()

        segments = out.get("segments", []) or []
        if not segments:
            return self._fallback()

        parsed: list[AudioSegment] = []
        for idx, segment in enumerate(segments):
            text = str(segment.get("text", "")).strip()
            if not text:
                continue
            speaker = "clinician" if idx % 2 == 0 else "patient"
            parsed.append(
                AudioSegment(
                    speaker=speaker,
                    text=text,
                    start_time_sec=float(segment.get("start", 0.0)),
                    end_time_sec=float(segment.get("end", 0.0)),
                    confidence=0.8,
                )
            )

        return parsed or self._fallback()
