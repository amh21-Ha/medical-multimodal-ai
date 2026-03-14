from pathlib import Path
import shutil
import uuid

from utils.config import get_settings


class IngestionPipeline:
    """Persists uploaded artifacts to local storage root.

    In production, this can be replaced by encrypted object storage.
    """

    def store_artifact(self, src_path: str, prefix: str) -> str:
        settings = get_settings()
        target_dir = Path(settings.storage_root)
        target_dir.mkdir(parents=True, exist_ok=True)

        src = Path(src_path)
        target = target_dir / f"{prefix}-{uuid.uuid4()}{src.suffix.lower()}"
        shutil.copy2(src, target)
        return str(target)
