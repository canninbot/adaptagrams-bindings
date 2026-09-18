# Adaptagrams bindings for Python and R

This monorepo provides two independently installable native packages:
`pyadaptagrams` for Python and `adaptagrams` for R. Both accept native igraph
graphs directly, call the same C++ adapter over Adaptagrams, and return native
igraph graphs with geometry attached as attributes.

The Adaptagrams source is pinned at commit
`840ebcff20dbba36ad03a2160edf7cbaf9859984`. Development verification used
Python 3.14.6 with python-igraph 1.0.0, and R 4.5.1 with R igraph 1.6.0. The
names `pyadaptagrams` and `adaptagrams` had no matching PyPI or CRAN package on
2026-09-18.

## Implemented functionality

- libavoid orthogonal and polyline obstacle-avoiding routing
- libcola force-directed layout with libvpsc non-overlap constraints
- fixed connector coordinates, direction constraints, and named libavoid
  routing parameters
- native Python and R igraph round trips with graph, vertex, edge, order,
  multiplicity, directedness, and isolated vertices preserved
- ordinary records/data frames in addition to igraph
- `layout_graph()`, `route_edges()`, `avoid_overlaps()`,
  `layout_and_route()`, `layout_matrix()`, and `get_edge_routes()`

libtopology and libdialect are not exposed in version 0.1.0. General libvpsc
constraint construction is not yet public. libavoid self-loop routing is
rejected with an edge-indexed error; self-loops remain valid input to layout
and are ignored as force edges. No graph is simplified or deduplicated.

## Architecture

`cpp/include/adaptagrams/adapter.hpp` and `cpp/src/adapter.cpp` form the shared
native boundary. The adapter owns each libavoid router with RAII; the router in
turn owns its registered `ShapeRef` and `ConnRef` objects. Python uses pybind11
and scikit-build-core. R uses Rcpp. Both igraph adapters use only documented
language APIs, not private igraph C/C++ internals.

The pinned upstream checkout lives in `third_party/adaptagrams`. `r/vendor` is
a generated, byte-for-byte source snapshot needed to make the R source package
self-contained; regenerate it with `tools/sync_r_vendor.sh` after changing the
shared adapter or upstream pin. `python/vendor` serves the same source-package
purpose and is regenerated with `tools/sync_python_vendor.sh`.

## Python installation and use

From the repository root:

```sh
pip install ./python
```

The required native workflow is direct:

```python
import igraph as ig
import pyadaptagrams as ag

g = ig.Graph(n=3, edges=[(0, 1)], directed=True)
g.vs["name"] = ["A", "B", "C"]
g.vs["x"] = [0.0, 200.0, 100.0]
g.vs["y"] = [0.0, 0.0, 0.0]
g.vs["width"] = [80.0, 80.0, 40.0]
g.vs["height"] = [40.0, 40.0, 40.0]
g.es["edge_id"] = ["e1"]

routed = ag.route_edges(g, routing="orthogonal")
assert isinstance(routed, ig.Graph)
print(routed.es["adaptagrams_route"])
```

`C` is a real rectangular obstacle and the route avoids its interior. For a
combined layout and route:

```python
g = ig.Graph.Ring(5)
result = ag.layout_and_route(g, routing="orthogonal")
coordinates = ag.layout_matrix(result)
routes = ag.get_edge_routes(result)
layout = ig.Layout(coordinates.tolist())
```

Ordinary input uses mapping records. Python data frames work through their
`to_dict(orient="records")` adapter, so pandas is optional:

```python
result = ag.route_edges(
    [{"x": 0, "y": 0}, {"x": 100, "y": 0}],
    [{"source": 0, "target": 1}],
)
```

## R installation and use

Install from the monorepo or from the built R source archive:

```r
remotes::install_local("r")
```

```r
library(igraph)
library(adaptagrams)

vertices <- data.frame(
    name = c("A", "B", "C"),
    x = c(0, 200, 100), y = c(0, 0, 0),
    width = c(80, 80, 40), height = c(40, 40, 40)
)
edges <- data.frame(from = "A", to = "B", edge_id = "e1")
g <- igraph::graph_from_data_frame(edges, directed = TRUE, vertices = vertices)
routed <- route_edges(g, routing = "orthogonal")
stopifnot(igraph::is_igraph(routed))
print(igraph::edge_attr(routed, "adaptagrams_route"))
```

For ordinary R data frames, `source` and `target` are one-based indices.

```r
result <- layout_and_route(igraph::make_ring(5))
coordinates <- layout_matrix(result)
plot(result, layout = coordinates)

# plot.igraph does not consume custom connector paths. Draw them explicitly.
for (route in igraph::edge_attr(result, "adaptagrams_route")) {
    lines(route[, 1], route[, 2])
}
```

## Geometry and attributes

Coordinates represent rectangle centers. Width and height default to 40 and
30. libavoid follows screen/SVG coordinates, where positive y points down.
Routing prefers `adaptagrams_x`/`adaptagrams_y`, then `x`/`y`; callers may
select another pair explicitly. Layout writes `adaptagrams_x` and
`adaptagrams_y`. It writes `x` and `y` only with `overwrite=True` in Python or
`overwrite = TRUE` in R.

`adaptagrams_route` is an ordered list of `(x, y)` pairs in Python and an
edge-level list of two-column numeric matrices in R. The default call copies
Python graphs; R already has value semantics. Existing metadata is retained.
The reserved computed route attribute is refreshed on repeated routing calls;
an existing custom output attribute name is rejected rather than overwritten.

Ports are supplied as edge-level coordinate pairs via
`source_port_attribute` and `target_port_attribute`. Direction attributes may
contain `up`, `down`, `left`, `right`, `all`, pipe/comma combinations, or the
libavoid bit flags 0 through 15. Supported routing parameter names are
`segment_penalty`, `angle_penalty`, `crossing_penalty`,
`cluster_crossing_penalty`, `fixed_shared_path_penalty`,
`port_direction_penalty`, `shape_buffer_distance`,
`ideal_nudging_distance`, and `reverse_direction_penalty`.

See [the igraph integration guide](docs/igraph-integration.md) and
[`examples/export_svg.py`](examples/export_svg.py) for further examples.

## Development and verification

```sh
uv venv .venv
uv pip install --python .venv/bin/python -e 'python[test]'
.venv/bin/pytest -q python/tests
uvx ruff check python/src python/tests

cmake -S . -B build/cpp -DADAPTAGRAMS_BUILD_PYTHON=OFF \
    -DADAPTAGRAMS_BUILD_CPP_TESTS=ON
cmake --build build/cpp --parallel
ctest --test-dir build/cpp --output-on-failure

tools/sync_r_vendor.sh
R CMD build r
R CMD check --no-manual adaptagrams_0.1.0.tar.gz
```

Benchmark drivers are under `benchmarks/`. They record timings and runtime
versions but no fabricated results are checked in. Graph sizes are configurable
because 10,000-node libcola layouts can be impractical on smaller machines.

## Platform status

Linux x86-64 is locally verified. GitHub Actions configures Linux, macOS, and
Windows builds; those platforms are CI targets, not locally verified claims.
The toolchain requires a C++17 compiler and CMake 3.18 or newer. Python wheels
and an sdist can be created with `python -m build python`; R uses standard
source package tooling.

## Licensing

Adaptagrams is LGPL-2.1-or-later. The binding code is distributed under the
same terms. See `LICENSES/` for the upstream license and dependency notices.
Distributors of binaries must preserve notices, provide the corresponding
LGPL-covered source (including modifications), and permit relinking as required
by the LGPL; merely bundling a binary does not satisfy all obligations.
