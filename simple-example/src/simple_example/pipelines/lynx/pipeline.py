from kedro.pipeline import Node, Pipeline

from .nodes import flag_protected, reproject, summarise, to_points


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            Node(to_points, "lynx_observations", "lynx_points", name="to_points"),
            Node(
                reproject,
                ["lynx_points", "params:target_crs"],
                "lynx_points_projected",
                name="reproject_points",
            ),
            Node(
                reproject,
                ["natura2000_sites", "params:target_crs"],
                "natura2000_projected",
                name="reproject_sites",
            ),
            Node(
                flag_protected,
                ["lynx_points_projected", "natura2000_projected"],
                "lynx_points_flagged",
                name="flag_protected",
            ),
            Node(
                summarise, "lynx_points_flagged", "protection_summary", name="summarise"
            ),
        ]
    )
