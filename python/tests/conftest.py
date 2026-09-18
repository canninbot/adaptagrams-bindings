"""Shared Python igraph fixtures and geometry assertions."""

import copy

import igraph as ig
import pytest


@pytest.fixture
def obstacle_graph() -> ig.Graph:
    """Create A-to-B with unrelated obstacle C between them.

    Returns:
        A directed igraph graph with fixed center-based geometry.
    """
    graph = ig.Graph(n=3, edges=[(0, 1)], directed=True)
    graph["project"] = "preserved"
    graph.vs["name"] = ["A", "B", "C"]
    graph.vs["x"] = [0.0, 200.0, 100.0]
    graph.vs["y"] = [0.0, 0.0, 0.0]
    graph.vs["width"] = [80.0, 80.0, 40.0]
    graph.vs["height"] = [40.0, 40.0, 40.0]
    graph.vs["color"] = ["red", "blue", "gray"]
    graph.es["edge_id"] = ["e1"]
    graph.es["weight"] = [2.5]
    return graph


@pytest.fixture
def biological_graph() -> ig.Graph:
    """Create the documented biochemical routing fixture.

    Returns:
        A directed A-to-R-to-B graph with obstacle C and SBGN metadata.
    """
    graph = ig.Graph(n=4, edges=[(0, 1), (1, 2)], directed=True)
    graph["model_id"] = "reaction-1"
    graph.vs["name"] = ["A", "R", "B", "C"]
    graph.vs["sbgn_class"] = [
        "macromolecule",
        "process",
        "macromolecule",
        "simple chemical",
    ]
    graph.vs["x"] = [0.0, 100.0, 240.0, 170.0]
    graph.vs["y"] = [0.0, 0.0, 0.0, 0.0]
    graph.vs["width"] = [60.0, 20.0, 60.0, 50.0]
    graph.vs["height"] = [40.0, 20.0, 40.0, 50.0]
    graph.vs["compartment"] = ["cytosol"] * 4
    graph.es["edge_id"] = ["consumption-1", "production-1"]
    graph.es["sbgn_arc_class"] = ["consumption", "production"]
    return graph


def graph_snapshot(graph: ig.Graph) -> dict:
    """Capture identity-sensitive topology and attributes.

    Args:
        graph: Graph to inspect.

    Returns:
        A deep-copied snapshot suitable for equality checks.
    """
    return {
        "vcount": graph.vcount(),
        "ecount": graph.ecount(),
        "directed": graph.is_directed(),
        "edges": graph.get_edgelist(),
        "graph_attributes": {
            name: copy.deepcopy(graph[name]) for name in graph.attributes()
        },
        "vertex_attributes": {
            name: copy.deepcopy(graph.vs[name]) for name in graph.vs.attributes()
        },
        "edge_attributes": {
            name: copy.deepcopy(graph.es[name]) for name in graph.es.attributes()
        },
    }


def assert_preserved(before: dict, after: ig.Graph) -> None:
    """Assert exact graph structure and original-attribute preservation.

    Args:
        before: Snapshot returned by graph_snapshot.
        after: Adaptagrams result graph.
    """
    assert after.vcount() == before["vcount"]
    assert after.ecount() == before["ecount"]
    assert after.is_directed() == before["directed"]
    assert after.get_edgelist() == before["edges"]
    for name, value in before["graph_attributes"].items():
        assert after[name] == value
    for name, value in before["vertex_attributes"].items():
        assert after.vs[name] == value
    for name, value in before["edge_attributes"].items():
        assert after.es[name] == value


def segment_intersects_rectangle_interior(
    first: tuple[float, float],
    second: tuple[float, float],
    center: tuple[float, float],
    size: tuple[float, float],
    tolerance: float = 1e-9,
) -> bool:
    """Return whether a line segment crosses an axis-aligned interior.

    Args:
        first: First segment point.
        second: Second segment point.
        center: Rectangle center.
        size: Rectangle width and height.
        tolerance: Interior-boundary tolerance.

    Returns:
        True when the open rectangle interior is intersected.
    """
    min_x = center[0] - size[0] / 2.0 + tolerance
    max_x = center[0] + size[0] / 2.0 - tolerance
    min_y = center[1] - size[1] / 2.0 + tolerance
    max_y = center[1] + size[1] / 2.0 - tolerance
    delta_x = second[0] - first[0]
    delta_y = second[1] - first[1]
    lower, upper = 0.0, 1.0
    for origin, delta, minimum, maximum in (
        (first[0], delta_x, min_x, max_x),
        (first[1], delta_y, min_y, max_y),
    ):
        if abs(delta) <= tolerance:
            if not minimum < origin < maximum:
                return False
            continue
        entry = (minimum - origin) / delta
        exit_ = (maximum - origin) / delta
        lower = max(lower, min(entry, exit_))
        upper = min(upper, max(entry, exit_))
    return lower < upper and upper > 0.0 and lower < 1.0


def assert_route_avoids(
    route: list[tuple[float, float]],
    center: tuple[float, float],
    size: tuple[float, float],
) -> None:
    """Assert every route segment avoids a rectangle interior.

    Args:
        route: Ordered connector points.
        center: Obstacle center.
        size: Obstacle width and height.
    """
    assert len(route) >= 2
    assert not any(
        segment_intersects_rectangle_interior(first, second, center, size)
        for first, second in zip(route, route[1:])
    )
