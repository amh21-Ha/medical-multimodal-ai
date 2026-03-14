from data.schemas import AnalysisResult


class DiscrepancyReportGenerator:
    def render(self, result: AnalysisResult) -> str:
        if not result.discrepancies:
            return "No clinically significant discrepancies were detected across text, video, and audio modalities."

        lines = ["Multimodal Discrepancy Summary", ""]
        for idx, item in enumerate(result.discrepancies, start=1):
            lines.append(f"{idx}. Type: {item.discrepancy_type}")
            lines.append(f"   Severity: {item.severity}")
            lines.append(f"   Confidence: {item.confidence:.2f}")
            lines.append(f"   Summary: {item.summary}")
            if item.supporting_evidence:
                lines.append("   Evidence:")
                for ev in item.supporting_evidence:
                    lines.append(f"   - {ev}")
            lines.append("")

        return "\n".join(lines).strip()
