"""igraph identity and validation tests."""

import igraph as ig
import pytest
from conftest import assert_preserved, graph_snapshot

import pyadaptagrams as ag


@pytest.mark.parametrize("directed", [True, False])
def test_topology_and_attributes_are_preserved(directed: bool) -> None:
    graph = ig.Graph(n=4, edges=[(0, 1), (0, 1), (2, 1)], directed=directed)
    graph["label"] = "network"
    graph.vs["name"] = ["duplicate", "duplicate", "C", "isolated"]
    graph.vs["type"] = [1, 2, 3, 4]
    graph.vs["x"] = [0.0, 100.0, 50.0, 200.0]
    graph.vs["y"] = [0.0, 0.0, 80.0, 100.0]
    graph.es["label"] = ["a", "b", "c"]
    before = graph_snapshot(graph)
    result = ag.layout_and_route(graph)
    assert_preserved(before, result)


def test_default_copy_keeps_input_immutable(obstacle_graph: ig.Graph) -> None:
    before = graph_snapshot(obstacle_graph)
    result = ag.route_edges(obstacle_graph)
    assert result is not obstacle_graph
    assert graph_snapshot(obstacle_graph) == before


def test_copy_false_explicitly_mutates(obstacle_graph: ig.Graph) -> None:
    result = ag.route_edges(obstacle_graph, copy=False)
    assert result is obstacle_graph
    assert "adaptagrams_route" in obstacle_graph.es.attributes()


def test_missing_names_uses_internal_indices() -> None:
    graph = ig.Graph(n=2, edges=[(0, 1)])
    graph.vs["x"] = [0.0, 100.0]
    graph.vs["y"] = [0.0, 0.0]
    assert "name" not in graph.vs.attributes()
    result = ag.route_edges(graph)
    assert result.get_edgelist() == [(0, 1)]
    assert result.es["adaptagrams_edge_id"] == ["edge-0"]


@pytest.mark.parametrize(
    ("attribute", "values", "message"),
    [
        ("x", [float("nan"), 1.0], "finite"),
        ("y", [0.0, float("inf")], "finite"),
        ("width", [-1.0, 10.0], "positive"),
        ("height", [10.0, 0.0], "positive"),
    ],
)
def test_invalid_geometry(attribute: str, values: list[float], message: str) -> None:
    graph = ig.Graph(n=2, edges=[(0, 1)])
    graph.vs["x"] = [0.0, 100.0]
    graph.vs["y"] = [0.0, 0.0]
    graph.vs[attribute] = values
    with pytest.raises(ag.GeometryError, match=message):
        ag.route_edges(graph)


def test_missing_and_partial_coordinates() -> None:
    graph = ig.Graph(n=2, edges=[(0, 1)])
    with pytest.raises(ag.GeometryError, match="routing requires"):
        ag.route_edges(graph)
    graph.vs["x"] = [0.0, 1.0]
    with pytest.raises(ag.GeometryError, match="must both be present"):
        ag.route_edges(graph)


def test_computed_coordinates_are_preferred_and_defaults_apply() -> None:
    graph = ig.Graph(n=2, edges=[(0, 1)])
    graph.vs["x"] = [1000.0, 1100.0]
    graph.vs["y"] = [1000.0, 1000.0]
    graph.vs["adaptagrams_x"] = [0.0, 100.0]
    graph.vs["adaptagrams_y"] = [0.0, 0.0]
    result = ag.route_edges(graph)
    route = result.es["adaptagrams_route"][0]
    assert route[0] == pytest.approx((0.0, 0.0))
    assert route[-1] == pytest.approx((100.0, 0.0))


def test_repeated_native_calls_reuse_output(obstacle_graph: ig.Graph) -> None:
    result = ag.layout_graph(obstacle_graph)
    result = ag.route_edges(result)
    second = ag.route_edges(result)
    assert second.es["adaptagrams_route"]
    assert result.get_edgelist() == second.get_edgelist()
