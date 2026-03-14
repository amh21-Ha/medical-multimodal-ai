from models.nlp.medical_report_parser import MedicalReportParser


def test_parser_extracts_knee_procedure() -> None:
    parser = MedicalReportParser()
    findings = parser.parse(
        patient_id="p1",
        report_text="Patient reports knee pain. Left knee tested with Lachman.",
    )

    assert findings.patient_id == "p1"
    assert any("knee" in proc.value.lower() for proc in findings.procedures)
