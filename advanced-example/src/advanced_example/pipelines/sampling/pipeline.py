from kedro.pipeline import Node, Pipeline

from .nodes import (
    background_sites,
    combine_sites,
    construction_sites,
    reproject,
    sample_polygons,
)


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            Node(
                reproject,
                ["construction_polygons", "params:crs"],
                "polygons_projected",
                name="reproject_polygons",
            ),
            Node(
                sample_polygons,
                ["polygons_projected", "params:sampling"],
                "selected_polygons",
                name="sample_polygons",
            ),
            Node(
                construction_sites,
                ["selected_polygons", "params:sampling"],
                "construction_sites",
                name="construction_sites",
            ),
            Node(
                background_sites,
                ["selected_polygons", "polygons_projected", "params:sampling"],
                "background_sites",
                name="background_sites",
            ),
            Node(
                combine_sites,
                ["construction_sites", "background_sites"],
                "sampling_sites",
                name="combine_sites",
            ),
        ]
    )
