from pipelines.orchestration_pipeline import OrchestrationPipeline


class RetrainingPipeline:
    """Placeholder retraining pipeline.

    Extend this with dataset retrieval, training loops, and evaluation gates.
    """

    def trigger(self) -> str:
        _ = OrchestrationPipeline
        return "retraining-triggered"
