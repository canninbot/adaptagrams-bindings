"""Adaptagrams layout and routing with native igraph integration."""

from .exceptions import AdaptagramsError, GeometryError, UnsupportedGraphError
from .layout import (
    avoid_overlaps,
    get_edge_routes,
    layout_and_route,
    layout_graph,
    layout_matrix,
)
from .routing import route_edges

__all__ = [
    "AdaptagramsError",
    "GeometryError",
    "UnsupportedGraphError",
    "avoid_overlaps",
    "get_edge_routes",
    "layout_and_route",
    "layout_graph",
    "layout_matrix",
    "route_edges",
]

__version__ = "0.1.0"
