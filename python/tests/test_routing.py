"""Native routing behavior tests."""

import math

import igraph as ig
import pytest
from conftest import assert_route_avoids

import pyadaptagrams as ag


def test_required_routing_example(obstacle_graph: ig.Graph) -> None:
    routed = ag.route_edges(obstacle_graph, routing="orthogonal")
    assert isinstance(routed, ig.Graph)
    assert routed.vcount() == obstacle_graph.vcount()
    assert routed.ecount() == obstacle_graph.ecount()
    assert "adaptagrams_route" in routed.es.attributes()
    assert_route_avoids(routed.es["adaptagrams_route"][0], (100.0, 0.0), (40.0, 40.0))


def test_orthogonal_segments(obstacle_graph: ig.Graph) -> None:
    route = ag.route_edges(obstacle_graph).es["adaptagrams_route"][0]
    for first, second in zip(route, route[1:]):
        assert first[0] == pytest.approx(second[0], abs=1e-9) or first[
            1
        ] == pytest.approx(second[1], abs=1e-9)


def test_polyline_is_finite_and_avoids_obstacle(obstacle_graph: ig.Graph) -> None:
    route = ag.route_edges(obstacle_graph, routing="polyline").es["adaptagrams_route"][
        0
    ]
    assert all(math.isfinite(value) for point in route for value in point)
    assert_route_avoids(route, (100.0, 0.0), (40.0, 40.0))


def test_parallel_edges_remain_addressable() -> None:
    graph = ig.Graph(n=2, edges=[(0, 1), (0, 1)], directed=True)
    graph.vs["x"] = [0.0, 100.0]
    graph.vs["y"] = [0.0, 0.0]
    graph.es["edge_id"] = ["first", "second"]
    result = ag.route_edges(graph)
    assert result.ecount() == 2
    assert result.es["edge_id"] == ["first", "second"]
    assert len(result.es["adaptagrams_route"]) == 2


def test_self_loop_has_specific_error_and_does_not_mutate() -> None:
    graph = ig.Graph(n=1, edges=[(0, 0)], directed=True)
    graph.vs["x"] = [0.0]
    graph.vs["y"] = [0.0]
    before = graph.copy()
    with pytest.raises(ag.UnsupportedGraphError, match="edge 0.*self-loop"):
        ag.route_edges(graph)
    assert graph.get_edgelist() == before.get_edgelist()
    assert graph.vs.attributes() == before.vs.attributes()


def test_fixed_ports_directions_and_parameters(obstacle_graph: ig.Graph) -> None:
    obstacle_graph.es["source_port"] = [(40.0, 0.0)]
    obstacle_graph.es["target_port"] = [(160.0, 0.0)]
    obstacle_graph.es["source_direction"] = ["right"]
    obstacle_graph.es["target_direction"] = ["left"]
    result = ag.route_edges(
        obstacle_graph,
        source_port_attribute="source_port",
        target_port_attribute="target_port",
        source_direction_attribute="source_direction",
        target_direction_attribute="target_direction",
        routing_parameters={"shape_buffer_distance": 2.0, "segment_penalty": 50.0},
    )
    route = result.es["adaptagrams_route"][0]
    assert route[0] == pytest.approx((40.0, 0.0))
    assert route[-1] == pytest.approx((160.0, 0.0))


def test_ordinary_records_use_same_native_router() -> None:
    vertices = [
        {"x": 0.0, "y": 0.0, "width": 80.0, "height": 40.0},
        {"x": 200.0, "y": 0.0, "width": 80.0, "height": 40.0},
        {"x": 100.0, "y": 0.0, "width": 40.0, "height": 40.0},
    ]
    result = ag.route_edges(vertices, [{"source": 0, "target": 1}])
    assert len(result["routes"]) == 1
    assert result["edges"][0]["adaptagrams_edge_id"] == "edge-0"
    assert_route_avoids(result["routes"][0], (100.0, 0.0), (40.0, 40.0))
