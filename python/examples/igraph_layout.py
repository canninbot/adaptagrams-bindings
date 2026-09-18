"""Run the documented native igraph layout-and-route example."""

import igraph as ig

import pyadaptagrams as ag

graph = ig.Graph.Ring(5)
result = ag.layout_and_route(graph, routing="orthogonal")
assert isinstance(result, ig.Graph)
print(ag.layout_matrix(result))
print(ag.get_edge_routes(result))
