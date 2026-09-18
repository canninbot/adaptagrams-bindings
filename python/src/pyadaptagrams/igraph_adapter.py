"""Conversion between public igraph objects and common native structures."""

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from . import _native
from .exceptions import GeometryError, UnsupportedGraphError

DEFAULT_WIDTH = 40.0
DEFAULT_HEIGHT = 30.0
_DIRECTIONS = {
    "none": 0,
    "up": 1,
    "down": 2,
    "left": 4,
    "right": 8,
    "all": 15,
}


@dataclass
class NativeInput:
    """Normalized input shared by routing and layout.

    Attributes:
        rectangles: Native center-based rectangular vertex geometry.
        edges: Native edges in original input order.
        vertex_records: Copies of ordinary vertex records, when applicable.
        edge_records: Copies of ordinary edge records, when applicable.
    """

    rectangles: list[Any]
    edges: list[Any]
    vertex_records: list[dict[str, Any]] | None = None
    edge_records: list[dict[str, Any]] | None = None


def is_igraph_graph(value: Any) -> bool:
    """Return whether value is an official python-igraph Graph.

    Args:
        value: Candidate object.

    Returns:
        True only for an igraph.Graph instance.
    """
    try:
        import igraph as ig
    except ImportError:
        return False
    return isinstance(value, ig.Graph)


def copy_graph(graph: Any, copy: bool) -> Any:
    """Return the requested output graph without changing topology.

    Args:
        graph: An igraph.Graph instance.
        copy: Whether to return a graph copy.

    Returns:
        A copied graph by default, or graph itself when copy is false.
    """
    return graph.copy() if copy else graph


def _records(value: Any, label: str) -> list[dict[str, Any]]:
    if hasattr(value, "to_dict"):
        try:
            value = value.to_dict(orient="records")
        except TypeError:
            pass
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
        raise TypeError(f"{label} must be an iterable of mappings")
    result = []
    for index, record in enumerate(value):
        if not isinstance(record, Mapping):
            raise TypeError(f"{label}[{index}] must be a mapping")
        result.append(dict(record))
    return result


def _float(value: Any, description: str) -> float:
    if isinstance(value, bool):
        raise GeometryError(f"{description} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise GeometryError(f"{description} must be numeric") from error
    if not math.isfinite(result):
        raise GeometryError(f"{description} must be finite")
    return result


def _dimensions(
    attributes: Sequence[str],
    values: Any,
    count: int,
    attribute: str,
    default: float,
) -> list[float]:
    if attribute not in attributes:
        return [default] * count
    result = []
    for index, value in enumerate(values[attribute]):
        dimension = _float(value, f"vertex {index} {attribute}")
        if dimension <= 0:
            raise GeometryError(f"vertex {index} {attribute} must be positive")
        result.append(dimension)
    return result


def _coordinate_names(
    attributes: Sequence[str],
    coordinate_attributes: tuple[str, str] | None,
    allow_missing: bool,
) -> tuple[str, str] | None:
    if coordinate_attributes is not None:
        x_attribute, y_attribute = coordinate_attributes
        present = (x_attribute in attributes, y_attribute in attributes)
        if present != (True, True):
            raise GeometryError(
                f"coordinate attributes {x_attribute!r} and {y_attribute!r} "
                "must both be present"
            )
        return coordinate_attributes
    for names in (("adaptagrams_x", "adaptagrams_y"), ("x", "y")):
        present = (names[0] in attributes, names[1] in attributes)
        if present == (True, True):
            return names
        if present[0] != present[1]:
            raise GeometryError(
                f"coordinate attributes {names[0]!r} and {names[1]!r} "
                "must both be present"
            )
    if allow_missing:
        return None
    raise GeometryError(
        "routing requires either adaptagrams_x/adaptagrams_y or x/y vertex attributes"
    )


def _initial_coordinates(
    count: int, ideal_edge_length: float
) -> list[tuple[float, float]]:
    if count == 0:
        return []
    if count == 1:
        return [(0.0, 0.0)]
    radius = max(ideal_edge_length, ideal_edge_length * count / (2.0 * math.pi))
    return [
        (
            radius * math.cos(2.0 * math.pi * index / count),
            radius * math.sin(2.0 * math.pi * index / count),
        )
        for index in range(count)
    ]


def _direction(value: Any, description: str) -> int:
    if value is None:
        return 15
    if isinstance(value, str):
        flags = 0
        for item in value.lower().replace("|", ",").split(","):
            name = item.strip()
            if name not in _DIRECTIONS:
                raise GeometryError(
                    f"{description} contains unknown direction {name!r}"
                )
            flags |= _DIRECTIONS[name]
        return flags
    if isinstance(value, int) and 0 <= value <= 15:
        return value
    raise GeometryError(f"{description} must be direction names or an integer 0..15")


def _point(value: Any, description: str) -> tuple[float, float] | None:
    if value is None:
        return None
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise GeometryError(f"{description} must be a two-item coordinate pair")
    if len(value) != 2:
        raise GeometryError(f"{description} must contain exactly two coordinates")
    return _float(value[0], description), _float(value[1], description)


def _native_edge(
    source: int,
    target: int,
    index: int,
    source_point: Any = None,
    target_point: Any = None,
    source_direction: Any = None,
    target_direction: Any = None,
) -> Any:
    edge = _native.Edge(source, target)
    parsed_source = _point(source_point, f"edge {index} source port")
    if parsed_source is not None:
        edge.has_source_point = True
        edge.source_point = _native.Point(*parsed_source)
    parsed_target = _point(target_point, f"edge {index} target port")
    if parsed_target is not None:
        edge.has_target_point = True
        edge.target_point = _native.Point(*parsed_target)
    edge.source_directions = _direction(
        source_direction, f"edge {index} source direction"
    )
    edge.target_directions = _direction(
        target_direction, f"edge {index} target direction"
    )
    return edge


def from_igraph(
    graph: Any,
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
) -> NativeInput:
    """Convert an igraph.Graph to stable index-based native structures.

    Args:
        graph: Official igraph.Graph object.
        require_coordinates: Whether missing coordinates are an error.
        coordinate_attributes: Explicit coordinate attribute names.
        width_attribute: Vertex width attribute.
        height_attribute: Vertex height attribute.
        default_width: Width used when the attribute is absent.
        default_height: Height used when the attribute is absent.
        ideal_edge_length: Scale used for deterministic initial positions.
        source_port_attribute: Optional edge source-port attribute.
        target_port_attribute: Optional edge target-port attribute.
        source_direction_attribute: Optional source direction attribute.
        target_direction_attribute: Optional target direction attribute.

    Returns:
        A normalized native input preserving vertex and edge order.
    """
    if not is_igraph_graph(graph):
        raise TypeError("graph must be an igraph.Graph")
    attributes = graph.vs.attributes()
    coordinate_names = _coordinate_names(
        attributes, coordinate_attributes, not require_coordinates
    )
    if coordinate_names is None:
        coordinates = _initial_coordinates(graph.vcount(), ideal_edge_length)
    else:
        coordinates = [
            (
                _float(x, f"vertex {index} {coordinate_names[0]}"),
                _float(y, f"vertex {index} {coordinate_names[1]}"),
            )
            for index, (x, y) in enumerate(
                zip(
                    graph.vs[coordinate_names[0]],
                    graph.vs[coordinate_names[1]],
                    strict=True,
                )
            )
        ]
    widths = _dimensions(
        attributes, graph.vs, graph.vcount(), width_attribute, default_width
    )
    heights = _dimensions(
        attributes, graph.vs, graph.vcount(), height_attribute, default_height
    )
    rectangles = [
        _native.Rectangle(x, y, width, height)
        for (x, y), width, height in zip(coordinates, widths, heights, strict=True)
    ]

    edge_attributes = graph.es.attributes()
    for attribute in (
        source_port_attribute,
        target_port_attribute,
        source_direction_attribute,
        target_direction_attribute,
    ):
        if attribute is not None and attribute not in edge_attributes:
            raise GeometryError(f"edge attribute {attribute!r} is missing")

    def edge_value(attribute: str | None, index: int) -> Any:
        return None if attribute is None else graph.es[index][attribute]

    edges = []
    for index, edge in enumerate(graph.es):
        source, target = edge.tuple
        if source == target and require_coordinates:
            raise UnsupportedGraphError(
                f"edge {index} is a self-loop; libavoid self-loop routing is "
                "unsupported (the input graph was not modified)"
            )
        edges.append(
            _native_edge(
                source,
                target,
                index,
                edge_value(source_port_attribute, index),
                edge_value(target_port_attribute, index),
                edge_value(source_direction_attribute, index),
                edge_value(target_direction_attribute, index),
            )
        )
    return NativeInput(rectangles, edges)


def from_records(
    vertices: Any,
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
) -> NativeInput:
    """Convert ordinary mapping records to the native representation.

    Args:
        vertices: Iterable of vertex mappings or a data frame.
        edges: Iterable of edge mappings with integer source and target.
        require_coordinates: Whether missing coordinates are an error.
        coordinate_attributes: Explicit coordinate fields.
        width_attribute: Vertex width field.
        height_attribute: Vertex height field.
        default_width: Missing-width default.
        default_height: Missing-height default.
        ideal_edge_length: Initial-position scale.
        source_port_attribute: Optional edge port field.
        target_port_attribute: Optional edge port field.
        source_direction_attribute: Optional direction field.
        target_direction_attribute: Optional direction field.

    Returns:
        Normalized input plus copied records.
    """
    vertex_records = _records(vertices, "vertices")
    edge_records = _records(edges, "edges")
    attribute_names = set().union(*(record.keys() for record in vertex_records))
    names = _coordinate_names(
        tuple(attribute_names), coordinate_attributes, not require_coordinates
    )
    if names is None:
        coordinates = _initial_coordinates(len(vertex_records), ideal_edge_length)
    else:
        coordinates = []
        for index, record in enumerate(vertex_records):
            if names[0] not in record or names[1] not in record:
                raise GeometryError(f"vertex {index} is missing coordinate fields")
            coordinates.append(
                (
                    _float(record[names[0]], f"vertex {index} {names[0]}"),
                    _float(record[names[1]], f"vertex {index} {names[1]}"),
                )
            )
    rectangles = []
    for index, (record, (x, y)) in enumerate(
        zip(vertex_records, coordinates, strict=True)
    ):
        width = _float(
            record.get(width_attribute, default_width), f"vertex {index} width"
        )
        height = _float(
            record.get(height_attribute, default_height), f"vertex {index} height"
        )
        if width <= 0 or height <= 0:
            raise GeometryError(f"vertex {index} width and height must be positive")
        rectangles.append(_native.Rectangle(x, y, width, height))
    native_edges = []
    for index, record in enumerate(edge_records):
        if "source" not in record or "target" not in record:
            raise GeometryError(f"edge {index} requires source and target fields")
        source, target = record["source"], record["target"]
        if not isinstance(source, int) or not isinstance(target, int):
            raise GeometryError(
                f"edge {index} source and target must be integer indices"
            )
        if (
            source < 0
            or target < 0
            or source >= len(rectangles)
            or target >= len(rectangles)
        ):
            raise GeometryError(f"edge {index} references an invalid vertex index")
        if source == target and require_coordinates:
            raise UnsupportedGraphError(
                f"edge {index} is a self-loop; routing is unsupported"
            )
        native_edges.append(
            _native_edge(
                source,
                target,
                index,
                record.get(source_port_attribute) if source_port_attribute else None,
                record.get(target_port_attribute) if target_port_attribute else None,
                record.get(source_direction_attribute)
                if source_direction_attribute
                else None,
                record.get(target_direction_attribute)
                if target_direction_attribute
                else None,
            )
        )
    return NativeInput(rectangles, native_edges, vertex_records, edge_records)
