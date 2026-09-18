"""Reproducible pyadaptagrams conversion/layout/routing benchmark."""

import argparse
import json
import platform
import time
import tracemalloc

import igraph as ig
import pyadaptagrams as ag
from pyadaptagrams import _native
from pyadaptagrams.igraph_adapter import from_igraph


def timed(function):
    """Measure one callable and peak Python-tracked memory.

    Args:
        function: Zero-argument callable to run.

    Returns:
        Pair of elapsed seconds and peak tracked bytes.
    """
    tracemalloc.start()
    started = time.perf_counter()
    value = function()
    elapsed = time.perf_counter() - started
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return value, elapsed, peak_bytes


def graph_fixture(size: int) -> ig.Graph:
    """Build a deterministic ring fixture.

    Args:
        size: Vertex count.

    Returns:
        A graph with fixed rectangular geometry.
    """
    graph = ig.Graph.Ring(size)
    layout = graph.layout_circle()
    graph.vs["x"] = [point[0] * size * 10 for point in layout]
    graph.vs["y"] = [point[1] * size * 10 for point in layout]
    graph.vs["width"] = [20.0] * size
    graph.vs["height"] = [14.0] * size
    return graph


def benchmark(size: int) -> dict:
    """Benchmark conversion, layout, routing, and end-to-end execution.

    Args:
        size: Graph vertex count.

    Returns:
        JSON-serializable timing and memory record.
    """
    graph = graph_fixture(size)
    normalized, conversion_seconds, conversion_bytes = timed(
        lambda: from_igraph(
            graph,
            require_coordinates=True,
            coordinate_attributes=None,
            width_attribute="width",
            height_attribute="height",
            default_width=40.0,
            default_height=30.0,
            ideal_edge_length=100.0,
        )
    )
    layout_options = _native.LayoutOptions()
    _, layout_seconds, layout_bytes = timed(
        lambda: _native.layout_graph(
            normalized.rectangles, normalized.edges, layout_options
        )
    )
    routing_options = _native.RoutingOptions()
    _, routing_seconds, routing_bytes = timed(
        lambda: _native.route_edges(
            normalized.rectangles, normalized.edges, routing_options
        )
    )
    _, total_seconds, total_bytes = timed(lambda: ag.layout_and_route(graph))
    return {
        "vertices": size,
        "edges": graph.ecount(),
        "conversion_seconds": conversion_seconds,
        "layout_seconds": layout_seconds,
        "routing_seconds": routing_seconds,
        "total_seconds": total_seconds,
        "peak_python_bytes": max(
            conversion_bytes, layout_bytes, routing_bytes, total_bytes
        ),
    }


def main() -> None:
    """Parse arguments, execute benchmarks, and print JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-s",
        "--sizes",
        nargs="+",
        type=int,
        default=[10, 100, 1000, 10000],
    )
    args = parser.parse_args()
    report = {
        "python": platform.python_version(),
        "python_igraph": ig.__version__,
        "platform": platform.platform(),
        "results": [benchmark(size) for size in args.sizes],
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
