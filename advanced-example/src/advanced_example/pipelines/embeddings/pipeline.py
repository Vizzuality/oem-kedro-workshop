from kedro.pipeline import Node, Pipeline

from .nodes import extract_embeddings


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            Node(
                extract_embeddings,
                ["sampling_sites", "tessera", "params:years"],
                "training_pixels",
                name="extract_embeddings",
            ),
        ]
    )
