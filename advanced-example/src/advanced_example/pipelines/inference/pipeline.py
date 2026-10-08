from kedro.pipeline import Node, Pipeline

from .nodes import area_window, classify_area


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            Node(
                area_window,
                ["tessera", "params:inference.bbox"],
                "inference_window",
                name="area_window",
            ),
            Node(
                classify_area,
                [
                    "tessera",
                    "construction_model",
                    "inference_window",
                    "params:years",
                    "params:inference.tile_size",
                ],
                "construction_probability",
                name="classify_area",
            ),
        ]
    )
