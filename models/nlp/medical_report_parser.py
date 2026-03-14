from __future__ import annotations

from collections import defaultdict
from typing import Any

from data.schemas import EvidenceItem, TextFindings

try:
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover
    pipeline = None


class MedicalReportParser:
    """Baseline NLP parser with deterministic extraction hooks.

    Uses a Hugging Face NER model when available, with deterministic fallback.
    """

    def __init__(self) -> None:
        self._ner = None
        if pipeline is not None:
            try:
                self._ner = pipeline(
                    task="token-classification",
                    model="d4data/biomedical-ner-all",
                    aggregation_strategy="simple",
                )
            except Exception:
                self._ner = None

    def _heuristic_parse(self, patient_id: str, report_text: str) -> TextFindings:
        text = report_text.lower()

        symptoms: list[EvidenceItem] = []
        findings: list[EvidenceItem] = []
        diagnoses: list[EvidenceItem] = []
        procedures: list[EvidenceItem] = []

        if "knee pain" in text:
            symptoms.append(EvidenceItem(value="knee pain", confidence=0.92))
        if "limited range of motion" in text:
            findings.append(EvidenceItem(value="limited range of motion", confidence=0.9))
        if "acl" in text:
            diagnoses.append(EvidenceItem(value="ACL injury", confidence=0.87))
        if "lachman" in text or "left knee tested" in text:
            procedures.append(EvidenceItem(value="left knee exam", confidence=0.85))

        return TextFindings(
            patient_id=patient_id,
            symptoms=symptoms,
            exam_findings=findings,
            diagnoses=diagnoses,
            procedures=procedures,
        )

    def _model_parse(self, patient_id: str, report_text: str) -> TextFindings:
        if self._ner is None:
            return self._heuristic_parse(patient_id, report_text)

        try:
            entities: list[dict[str, Any]] = self._ner(report_text)
        except Exception:
            return self._heuristic_parse(patient_id, report_text)

        buckets: dict[str, list[EvidenceItem]] = defaultdict(list)
        for ent in entities:
            label = str(ent.get("entity_group", "")).lower()
            word = str(ent.get("word", "")).strip()
            score = float(ent.get("score", 0.5))
            if not word:
                continue

            item = EvidenceItem(value=word, confidence=max(0.0, min(1.0, score)))
            if any(key in label for key in ["sign", "symptom"]):
                buckets["symptoms"].append(item)
            elif any(key in label for key in ["disease", "diagnosis", "problem"]):
                buckets["diagnoses"].append(item)
            elif any(key in label for key in ["procedure", "treatment", "test"]):
                buckets["procedures"].append(item)
            else:
                buckets["exam_findings"].append(item)

        merged = self._heuristic_parse(patient_id, report_text)
        if buckets["symptoms"]:
            merged.symptoms = buckets["symptoms"]
        if buckets["exam_findings"]:
            merged.exam_findings = buckets["exam_findings"]
        if buckets["diagnoses"]:
            merged.diagnoses = buckets["diagnoses"]
        if buckets["procedures"]:
            merged.procedures = buckets["procedures"]
        return merged

    def parse(self, patient_id: str, report_text: str) -> TextFindings:
        return self._model_parse(patient_id, report_text)
