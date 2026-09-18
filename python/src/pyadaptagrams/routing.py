"""Obstacle-avoiding edge routing APIs."""

from typing import Any

from . import _native
from ._common import normalize_input
from .igraph_adapter import DEFAULT_HEIGHT, DEFAULT_WIDTH, copy_graph


def route_edges(
    graph_or_vertices: Any,
    edges: Any = None,
    *,
    routing: str = "orthogonal",
    copy: bool = True,
    coordinate_attributes: tuple[str, str] | None = None,
    width_attribute: str = "width",
    height_attribute: str = "height",
    default_width: float = DEFAULT_WIDTH,
    default_height: float = DEFAULT_HEIGHT,
    route_attribute: str = "adaptagrams_route",
    source_port_attribute: str | None = None,
    target_port_attribute: str | None = None,
    source_direction_attribute: str | None = None,
    target_direction_attribute: str | None = None,
    routing_parameters: dict[str, float] | None = None,
) -> Any:
    """Route graph edges around rectangular vertex obstacles.

    Coordinates are rectangle centers. Computed coordinates are preferred over
    x/y unless ``coordinate_attributes`` is explicit. The original igraph is
    unchanged when ``copy=True``.

    Args:
        graph_or_vertices: An igraph.Graph or vertex mapping records.
        edges: Edge records for ordinary input; omitted for igraph input.
        routing: Either ``"orthogonal"`` or ``"polyline"``.
        copy: Copy igraph input before adding routes.
        coordinate_attributes: Explicit x/y attribute pair.
        width_attribute: Vertex rectangle width attribute.
        height_attribute: Vertex rectangle height attribute.
        default_width: Width used when absent.
        default_height: Height used when absent.
        route_attribute: Output edge attribute name.
        source_port_attribute: Optional edge coordinate-pair attribute.
        target_port_attribute: Optional edge coordinate-pair attribute.
        source_direction_attribute: Optional libavoid direction attribute.
        target_direction_attribute: Optional libavoid direction attribute.
        routing_parameters: Supported named libavoid routing parameters.

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
        source_port_attribute=source_port_attribute,
        target_port_attribute=target_port_attribute,
        source_direction_attribute=source_direction_attribute,
        target_direction_attribute=target_direction_attribute,
    )
    options = _native.RoutingOptions()
    options.routing = routing
    options.parameters = routing_parameters or {}
    native_routes = _native.route_edges(
        normalized.rectangles, normalized.edges, options
    )
    routes = [[(point.x, point.y) for point in route] for route in native_routes]
    if is_igraph:
        result = copy_graph(graph_or_vertices, copy)
        if (
            route_attribute in result.es.attributes()
            and route_attribute != "adaptagrams_route"
        ):
            raise ValueError(
                f"edge attribute {route_attribute!r} already exists; choose a "
                "different route_attribute"
            )
        result.es[route_attribute] = routes
        if (
            "edge_id" not in result.es.attributes()
            and "adaptagrams_edge_id" not in result.es.attributes()
        ):
            result.es["adaptagrams_edge_id"] = [
                f"edge-{index}" for index in range(result.ecount())
            ]
        return result
    edge_records = normalized.edge_records or []
    has_identifiers = all("edge_id" in record for record in edge_records)
    return {
        "vertices": normalized.vertex_records,
        "edges": [
            {
                **record,
                **({} if has_identifiers else {"adaptagrams_edge_id": f"edge-{index}"}),
                route_attribute: route,
            }
            for index, (record, route) in enumerate(
                zip(edge_records, routes, strict=True)
            )
        ],
        "routes": routes,
    }
