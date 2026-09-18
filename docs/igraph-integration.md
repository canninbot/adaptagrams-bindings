# igraph integration

## Identity contract

Both adapters enumerate vertices and edges in native igraph order and use the
internal zero-based vertex indices at the C++ boundary. R's one-based indices
are converted internally. Names are metadata, never identity, so absent or
duplicate names are supported. Every connector is mapped by edge index; endpoint
pairs are deliberately not used as identifiers because parallel edges are
valid.

Directedness, stored endpoint order, parallel edges, isolated vertices, graph
attributes, and all unrelated vertex and edge attributes are preserved. No
adapter calls `simplify()`. Python returns a copy unless `copy=False`; R's
documented value semantics produce a modified copy.

## Geometry contract

`x`, `y`, `adaptagrams_x`, and `adaptagrams_y` are rectangle-center
coordinates. Width and height are full rectangle dimensions. Positive y points
down, matching libavoid and SVG. Routing chooses computed coordinates first so
the result of `layout_graph()` can immediately be routed. An explicit
coordinate pair overrides this selection.

Python route values are lists of coordinate pairs. R route values are list
attributes whose elements are numeric matrices with columns `x` and `y`.
`layout_matrix()` follows vertex order. `get_edge_routes()` returns edge-indexed
ordinary records/data frames without changing the graph.

## Python and R differences

Python ordinary edges use zero-based `source` and `target`; R ordinary edges
use one-based columns. Python exposes `copy=False` because igraph objects are
mutable. R relies on value semantics. Both language adapters call identical
native routing/layout functions, and neither links to igraph internals.

## Graph structures

Empty graphs, isolated vertices, directed/undirected graphs, missing names, and
parallel edges are supported. Layout accepts self-loops but omits them from the
libcola force graph. Routing self-loops is explicitly unsupported because the
current center-endpoint scheme does not provide a correct libavoid loop route;
an edge-specific exception is raised before native routing.

## Plotting

`igraph` plotting understands the coordinate matrix, but does not understand
`adaptagrams_route`. Plot vertices with `layout_matrix(result)` and render the
ordered connector points separately. The SVG example in `examples/` shows the
complete geometry path without suggesting automatic routed-edge support.
