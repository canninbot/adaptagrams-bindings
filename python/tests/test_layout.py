"""libcola layout and libvpsc overlap tests."""

import igraph as ig
import numpy as np

import pyadaptagrams as ag


def test_required_ring_example() -> None:
    graph = ig.Graph.Ring(5)
    result = ag.layout_and_route(graph, routing="orthogonal")
    assert isinstance(result, ig.Graph)
    coordinates = ag.layout_matrix(result)
    routes = ag.get_edge_routes(result)
    assert coordinates.shape == (5, 2)
    assert len(routes) == 5


def test_layout_matrix_follows_vertex_order_and_igraph_layout() -> None:
    graph = ig.Graph(n=3, edges=[(2, 0), (0, 1)])
    result = ag.layout_graph(graph)
    matrix = ag.layout_matrix(result)
    assert matrix[:, 0].tolist() == result.vs["adaptagrams_x"]
    assert matrix[:, 1].tolist() == result.vs["adaptagrams_y"]
    layout = ig.Layout(matrix.tolist())
    assert len(layout) == 3


def test_avoid_overlaps_uses_real_constraint_solver() -> None:
    graph = ig.Graph(n=2)
    graph.vs["x"] = [0.0, 0.0]
    graph.vs["y"] = [0.0, 0.0]
    graph.vs["width"] = [50.0, 50.0]
    graph.vs["height"] = [30.0, 30.0]
    result = ag.avoid_overlaps(graph)
    coordinates = ag.layout_matrix(result)
    separated_x = abs(coordinates[0, 0] - coordinates[1, 0]) >= 50.0 - 1e-7
    separated_y = abs(coordinates[0, 1] - coordinates[1, 1]) >= 30.0 - 1e-7
    assert separated_x or separated_y


def test_empty_graph_operations() -> None:
    graph = ig.Graph()
    laid_out = ag.layout_graph(graph)
    routed = (
        ag.route_edges(
            graph,
            coordinate_attributes=("x", "y"),
        )
        if "x" in graph.vs.attributes()
        else ag.layout_and_route(graph)
    )
    assert laid_out.vcount() == routed.vcount() == 0
    assert ag.layout_matrix(laid_out).shape == (0, 2)


def test_isolated_vertices_survive_layout() -> None:
    graph = ig.Graph(n=4, edges=[(0, 1)])
    result = ag.layout_and_route(graph)
    assert result.vcount() == 4
    assert result.ecount() == 1
    assert np.isfinite(ag.layout_matrix(result)).all()
