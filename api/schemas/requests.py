from pydantic import BaseModel, Field


class AnalyzeExamRequest(BaseModel):
    patient_id: str = Field(min_length=1)
    report_text: str = Field(min_length=1)
    video_path: str = Field(min_length=1)
    audio_path: str = Field(min_length=1)
