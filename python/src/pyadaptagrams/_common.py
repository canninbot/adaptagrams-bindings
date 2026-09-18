"""Shared public-API helpers."""

from typing import Any

from .igraph_adapter import NativeInput, from_igraph, from_records, is_igraph_graph


def normalize_input(
    graph_or_vertices: Any,
    edges: Any,
    *,
    require_coordinates: bool,
    coordinate_attributes: tuple[str, str] | None,
    width_attribute: str,
    height_attribute: str,
    default_width: float,
    default_height: float,
    ideal_edge_length: float,
    source_port_attribute: str | None = None,
    target_port_attribute: str | None = None,
    source_direction_attribute: str | None = None,
    target_direction_attribute: str | None = None,
) -> tuple[NativeInput, bool]:
    """Normalize either accepted input category.

    Args:
        graph_or_vertices: An igraph graph or ordinary vertex records.
        edges: Ordinary edge records, omitted for igraph input.
        require_coordinates: Whether coordinates must already exist.
        coordinate_attributes: Explicit coordinate attribute names.
        width_attribute: Width attribute or field.
        height_attribute: Height attribute or field.
        default_width: Missing-width default.
        default_height: Missing-height default.
        ideal_edge_length: Initial layout scale.
        source_port_attribute: Optional edge port attribute.
        target_port_attribute: Optional edge port attribute.
        source_direction_attribute: Optional edge direction attribute.
        target_direction_attribute: Optional edge direction attribute.

    Returns:
        Normalized data and whether the original input was igraph.
    """
    kwargs = {
        "require_coordinates": require_coordinates,
        "coordinate_attributes": coordinate_attributes,
        "width_attribute": width_attribute,
        "height_attribute": height_attribute,
        "default_width": default_width,
        "default_height": default_height,
        "ideal_edge_length": ideal_edge_length,
        "source_port_attribute": source_port_attribute,
        "target_port_attribute": target_port_attribute,
        "source_direction_attribute": source_direction_attribute,
        "target_direction_attribute": target_direction_attribute,
    }
    if is_igraph_graph(graph_or_vertices):
        if edges is not None:
            raise TypeError("edges must not be supplied with igraph input")
        return from_igraph(graph_or_vertices, **kwargs), True
    if edges is None:
        raise TypeError("ordinary vertex input requires an edges argument")
    return from_records(graph_or_vertices, edges, **kwargs), False
