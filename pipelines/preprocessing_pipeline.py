from data.validation import validate_media_file


class PreprocessingPipeline:
    def validate_inputs(self, video_path: str, audio_path: str) -> None:
        validate_media_file(video_path, kind="video")
        validate_media_file(audio_path, kind="audio")
