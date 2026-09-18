"""Constraint-based graph layout and geometry helpers."""

from typing import Any

import numpy as np

from . import _native
from ._common import normalize_input
from .igraph_adapter import DEFAULT_HEIGHT, DEFAULT_WIDTH, copy_graph, is_igraph_graph
from .routing import route_edges


def _layout_result(
    graph_or_vertices: Any,
    normalized: Any,
    is_igraph: bool,
    coordinates: list[tuple[float, float]],
    *,
    copy: bool,
    output_attributes: tuple[str, str],
    overwrite: bool,
) -> Any:
    if is_igraph:
        result = copy_graph(graph_or_vertices, copy)
        for attribute in output_attributes:
            if attribute in result.vs.attributes():
                raise ValueError(
                    f"vertex attribute {attribute!r} already exists; choose "
                    "different output_attributes"
                )
        result.vs[output_attributes[0]] = [point[0] for point in coordinates]
        result.vs[output_attributes[1]] = [point[1] for point in coordinates]
        if overwrite:
            result.vs["x"] = [point[0] for point in coordinates]
            result.vs["y"] = [point[1] for point in coordinates]
        return result
    vertex_records = normalized.vertex_records or []
    return {
        "vertices": [
            {
                **record,
                output_attributes[0]: coordinate[0],
                output_attributes[1]: coordinate[1],
                **({"x": coordinate[0], "y": coordinate[1]} if overwrite else {}),
            }
            for record, coordinate in zip(vertex_records, coordinates, strict=True)
        ],
        "edges": normalized.edge_records,
        "coordinates": coordinates,
    }


def layout_graph(
    graph_or_vertices: Any,
    edges: Any = None,
    *,
    copy: bool = True,
    coordinate_attributes: tuple[str, str] | None = None,
    width_attribute: str = "width",
    height_attribute: str = "height",
    default_width: float = DEFAULT_WIDTH,
    default_height: float = DEFAULT_HEIGHT,
    output_attributes: tuple[str, str] = ("adaptagrams_x", "adaptagrams_y"),
    overwrite: bool = False,
    ideal_edge_length: float = 100.0,
    avoid_node_overlaps: bool = True,
    max_iterations: int = 100,
) -> Any:
    """Lay out a graph with libcola and return the same input category.

    Args:
        graph_or_vertices: An igraph.Graph or vertex mapping records.
        edges: Ordinary edge records, omitted for igraph input.
        copy: Copy igraph input before adding coordinates.
        coordinate_attributes: Explicit initial coordinate attribute pair.
        width_attribute: Vertex width attribute.
        height_attribute: Vertex height attribute.
        default_width: Width used when absent.
        default_height: Height used when absent.
        output_attributes: Non-destructive output coordinate names.
        overwrite: Also replace x and y when true.
        ideal_edge_length: libcola ideal edge length.
        avoid_node_overlaps: Generate non-overlap constraints.
        max_iterations: Layout convergence iteration limit.

    Returns:
        A native igraph.Graph, or a dictionary for ordinary input.
    """
    normalized, is_igraph = normalize_input(
        graph_or_vertices,
        edges,
        require_coordinates=False,
        coordinate_attributes=coordinate_attributes,
        width_attribute=width_attribute,
        height_attribute=height_attribute,
        default_width=default_width,
        default_height=default_height,
        ideal_edge_length=ideal_edge_length,
    )
    options = _native.LayoutOptions()
    options.ideal_edge_length = ideal_edge_length
    options.avoid_overlaps = avoid_node_overlaps
    options.max_iterations = max_iterations
    native_coordinates = _native.layout_graph(
        normalized.rectangles, normalized.edges, options
    )
    coordinates = [(point.x, point.y) for point in native_coordinates]
    return _layout_result(
        graph_or_vertices,
        normalized,
        is_igraph,
        coordinates,
        copy=copy,
        output_attributes=output_attributes,
        overwrite=overwrite,
    )


def avoid_overlaps(
    graph_or_vertices: Any,
    edges: Any = None,
    *,
    copy: bool = True,
    coordinate_attributes: tuple[str, str] | None = None,
    width_attribute: str = "width",
    height_attribute: str = "height",
    default_width: float = DEFAULT_WIDTH,
    default_height: float = DEFAULT_HEIGHT,
    output_attributes: tuple[str, str] = ("adaptagrams_x", "adaptagrams_y"),
    overwrite: bool = False,
    max_iterations: int = 100,
) -> Any:
    """Remove rectangle overlaps using libcola/libvpsc constraints.

    Args:
        graph_or_vertices: An igraph.Graph or vertex mapping records.
        edges: Edge records for ordinary input.
        copy: Copy igraph input before adding coordinates.
        coordinate_attributes: Explicit initial coordinate pair.
        width_attribute: Vertex width attribute.
        height_attribute: Vertex height attribute.
        default_width: Width used when absent.
        default_height: Height used when absent.
        output_attributes: Output coordinate attribute names.
        overwrite: Also replace x and y when true.
        max_iterations: Solver iteration limit.

    Returns:
        A native igraph.Graph, or a dictionary for ordinary input.
    """
    normalized, is_igraph = normalize_input(
        graph_or_vertices,
        edges,
        require_coordinates=True,
        coordinate_attributes=coordinate_attributes,
        width_attribute=width_attribute,
        height_attribute=height_attribute,
        default_width=default_width,
        default_height=default_height,
        ideal_edge_length=100.0,
    )
    native_coordinates = _native.avoid_overlaps(normalized.rectangles, max_iterations)
    coordinates = [(point.x, point.y) for point in native_coordinates]
    return _layout_result(
        graph_or_vertices,
        normalized,
        is_igraph,
        coordinates,
        copy=copy,
        output_attributes=output_attributes,
        overwrite=overwrite,
    )


def layout_and_route(
    graph_or_vertices: Any,
    edges: Any = None,
    *,
    routing: str = "orthogonal",
    copy: bool = True,
    overwrite: bool = False,
    **kwargs: Any,
) -> Any:
    """Apply libcola layout followed by libavoid routing.

    Args:
        graph_or_vertices: An igraph.Graph or ordinary vertex records.
        edges: Ordinary edge records, omitted for igraph input.
        routing: ``"orthogonal"`` or ``"polyline"``.
        copy: Preserve igraph input by default.
        overwrite: Also write computed x/y coordinates.
        **kwargs: Options shared with layout_graph.

    Returns:
        A native igraph.Graph, or an ordinary structured result.
    """
    layout_keys = {
        "coordinate_attributes",
        "width_attribute",
        "height_attribute",
        "default_width",
        "default_height",
        "output_attributes",
        "ideal_edge_length",
        "avoid_node_overlaps",
        "max_iterations",
    }
    layout_kwargs = {key: value for key, value in kwargs.items() if key in layout_keys}
    route_kwargs = {
        key: value
        for key, value in kwargs.items()
        if key
        in {
            "width_attribute",
            "height_attribute",
            "default_width",
            "default_height",
            "route_attribute",
            "source_port_attribute",
            "target_port_attribute",
            "source_direction_attribute",
            "target_direction_attribute",
            "routing_parameters",
        }
    }
    unknown = set(kwargs) - layout_keys - set(route_kwargs)
    if unknown:
        names = ", ".join(sorted(unknown))
        raise TypeError(f"unexpected layout_and_route options: {names}")
    laid_out = layout_graph(
        graph_or_vertices,
        edges,
        copy=copy,
        overwrite=overwrite,
        **layout_kwargs,
    )
    if is_igraph_graph(laid_out):
        return route_edges(
            laid_out,
            routing=routing,
            copy=False,
            coordinate_attributes=("adaptagrams_x", "adaptagrams_y"),
            **route_kwargs,
        )
    return route_edges(
        laid_out["vertices"],
        laid_out["edges"],
        routing=routing,
        coordinate_attributes=("adaptagrams_x", "adaptagrams_y"),
        **route_kwargs,
    )


def layout_matrix(graph_or_result: Any) -> np.ndarray:
    """Return coordinates as an N-by-2 NumPy array in vertex order.

    Args:
        graph_or_result: An igraph graph or ordinary structured result.

    Returns:
        Float64 coordinates compatible with ``igraph.Layout``.
    """
    if is_igraph_graph(graph_or_result):
        attributes = graph_or_result.vs.attributes()
        if "adaptagrams_x" in attributes and "adaptagrams_y" in attributes:
            names = ("adaptagrams_x", "adaptagrams_y")
        elif "x" in attributes and "y" in attributes:
            names = ("x", "y")
        else:
            raise ValueError("graph has no complete coordinate attribute pair")
        return np.asarray(
            list(zip(graph_or_result.vs[names[0]], graph_or_result.vs[names[1]])),
            dtype=float,
        ).reshape((-1, 2))
    if isinstance(graph_or_result, dict) and "coordinates" in graph_or_result:
        return np.asarray(graph_or_result["coordinates"], dtype=float).reshape((-1, 2))
    raise TypeError("expected an igraph.Graph or structured Adaptagrams result")


def get_edge_routes(graph_or_result: Any) -> list[dict[str, Any]]:
    """Return edge-indexed route records in original edge order.

    Args:
        graph_or_result: An igraph graph or ordinary structured result.

    Returns:
        Records containing edge_index, source, target, and route.
    """
    if is_igraph_graph(graph_or_result):
        if "adaptagrams_route" not in graph_or_result.es.attributes():
            raise ValueError("graph has no adaptagrams_route edge attribute")
        return [
            {
                "edge_index": index,
                "source": edge.source,
                "target": edge.target,
                "route": edge["adaptagrams_route"],
            }
            for index, edge in enumerate(graph_or_result.es)
        ]
    if isinstance(graph_or_result, dict) and "routes" in graph_or_result:
        edges = graph_or_result.get("edges", [])
        return [
            {
                "edge_index": index,
                "source": edge["source"],
                "target": edge["target"],
                "route": route,
            }
            for index, (edge, route) in enumerate(
                zip(edges, graph_or_result["routes"], strict=True)
            )
        ]
    raise TypeError("expected an igraph.Graph or structured Adaptagrams result")
