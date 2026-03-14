from pathlib import Path

from utils.config import get_settings
from utils.errors import ValidationError


ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac"}


def validate_media_file(file_path: str, kind: str) -> None:
    path = Path(file_path)
    if not path.exists():
        raise ValidationError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    if kind == "video" and ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(f"Unsupported video extension: {ext}")
    if kind == "audio" and ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise ValidationError(f"Unsupported audio extension: {ext}")

    settings = get_settings()
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > settings.max_upload_mb:
        raise ValidationError(
            f"{kind} file exceeds {settings.max_upload_mb} MB limit: {size_mb:.2f} MB"
        )
