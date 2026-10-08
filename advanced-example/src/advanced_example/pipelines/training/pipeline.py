from kedro.pipeline import Node, Pipeline

from .nodes import evaluate_model, split_data, train_model


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            Node(
                split_data,
                ["training_pixels", "params:model"],
                ["train_pixels", "test_pixels"],
                name="split_data",
            ),
            Node(
                train_model,
                ["train_pixels", "params:model"],
                "construction_model",
                name="train_model",
            ),
            Node(
                evaluate_model,
                ["construction_model", "test_pixels"],
                "model_metrics",
                name="evaluate_model",
            ),
        ]
    )
