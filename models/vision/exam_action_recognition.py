from __future__ import annotations

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None

from data.schemas import VideoObservation

try:
    import torch
except Exception:  # pragma: no cover
    torch = None


class ExamActionRecognizer:
    """Baseline vision action recognizer.

    Uses OpenCV-based motion segmentation with optional torch tensor path.
    """

    def infer(self, video_path: str) -> list[VideoObservation]:
        if cv2 is None:
            return [
                VideoObservation(
                    action="vision_backend_unavailable",
                    body_region="unknown",
                    start_time_sec=0.0,
                    end_time_sec=0.0,
                    confidence=0.2,
                )
            ]

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return [
                VideoObservation(
                    action="unreadable_video",
                    body_region="unknown",
                    start_time_sec=0.0,
                    end_time_sec=0.0,
                    confidence=0.2,
                )
            ]

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        prev = None
        motion_windows: list[tuple[float, float]] = []
        current_start = None
        frame_idx = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            if prev is not None:
                diff = cv2.absdiff(prev, gray)
                motion_score = float(diff.mean())
                ts = frame_idx / fps

                if torch is not None:
                    _ = torch.tensor(motion_score)

                if motion_score > 8.0:
                    if current_start is None:
                        current_start = ts
                elif current_start is not None:
                    motion_windows.append((current_start, ts))
                    current_start = None

            prev = gray
            frame_idx += 1

        cap.release()

        if current_start is not None:
            motion_windows.append((current_start, frame_idx / fps))

        if not motion_windows:
            return [
                VideoObservation(
                    action="minimal_exam_activity",
                    body_region="unknown",
                    start_time_sec=0.0,
                    end_time_sec=max(frame_idx / fps, 0.0),
                    confidence=0.35,
                )
            ]

        observations: list[VideoObservation] = []
        for start, end in motion_windows[:5]:
            duration = max(end - start, 0.1)
            action = "general_physical_exam"
            body_region = "upper_extremity" if start < 30 else "lower_extremity"
            confidence = min(0.95, 0.55 + duration / 20)
            observations.append(
                VideoObservation(
                    action=action,
                    body_region=body_region,
                    start_time_sec=start,
                    end_time_sec=end,
                    confidence=confidence,
                )
            )

        return observations
