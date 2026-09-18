"""Run the documented native igraph routing example."""

import igraph as ig

import pyadaptagrams as ag

graph = ig.Graph(n=3, edges=[(0, 1)], directed=True)
graph.vs["name"] = ["A", "B", "C"]
graph.vs["x"] = [0.0, 200.0, 100.0]
graph.vs["y"] = [0.0, 0.0, 0.0]
graph.vs["width"] = [80.0, 80.0, 40.0]
graph.vs["height"] = [40.0, 40.0, 40.0]
graph.es["edge_id"] = ["e1"]

routed = ag.route_edges(graph, routing="orthogonal")
assert isinstance(routed, ig.Graph)
print(routed.es["adaptagrams_route"])
