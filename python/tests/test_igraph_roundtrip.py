"""Explicit igraph round-trip and biological fixture tests."""

import igraph as ig
from conftest import assert_preserved, assert_route_avoids, graph_snapshot

import pyadaptagrams as ag


def test_explicit_roundtrip(obstacle_graph: ig.Graph) -> None:
    before = graph_snapshot(obstacle_graph)
    routed = ag.route_edges(obstacle_graph)
    assert_preserved(before, routed)
    assert "adaptagrams_route" in routed.es.attributes()


def test_biological_network_preserves_identity_and_metadata(
    biological_graph: ig.Graph,
) -> None:
    before = graph_snapshot(biological_graph)
    routed = ag.route_edges(biological_graph)
    assert_preserved(before, routed)
    assert routed.vs["name"] == ["A", "R", "B", "C"]
    assert routed.vs["sbgn_class"][1] == "process"
    assert routed.es["sbgn_arc_class"] == ["consumption", "production"]
    assert routed.get_edgelist() == [(0, 1), (1, 2)]
    routes = routed.es["adaptagrams_route"]
    assert_route_avoids(routes[1], (170.0, 0.0), (50.0, 50.0))
    assert biological_graph.vs["x"] == [0.0, 100.0, 240.0, 170.0]
