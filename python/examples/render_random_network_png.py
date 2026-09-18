"""Render a random igraph network before and after orthogonal routing."""

import argparse
import random
from pathlib import Path

import igraph as ig
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

import pyadaptagrams as ag

NODE_COUNT = 14
RANDOM_SEED = 20260918
EXTRA_EDGE_COUNT = 12
NODE_WIDTH = 46.0
NODE_HEIGHT = 30.0


def random_network() -> ig.Graph:
    """Create a reproducible connected random network.

    Returns:
        An undirected igraph graph with rectangular node dimensions.
    """
    random_generator = random.Random(RANDOM_SEED)
    ring_edges = [(index, (index + 1) % NODE_COUNT) for index in range(NODE_COUNT)]
    ring_keys = {tuple(sorted(edge)) for edge in ring_edges}
    candidates = [
        (source, target)
        for source in range(NODE_COUNT)
        for target in range(source + 1, NODE_COUNT)
        if (source, target) not in ring_keys
    ]
    graph = ig.Graph(
        n=NODE_COUNT,
        edges=ring_edges + random_generator.sample(candidates, EXTRA_EDGE_COUNT),
        directed=False,
    )
    graph.vs["name"] = [str(index + 1) for index in range(NODE_COUNT)]
    graph.vs["width"] = [NODE_WIDTH] * NODE_COUNT
    graph.vs["height"] = [NODE_HEIGHT] * NODE_COUNT
    return graph


def drawing_bounds(
    graph: ig.Graph, routes: list[list[tuple[float, float]]]
) -> tuple[float, float, float, float]:
    """Calculate padded bounds containing every node and connector.

    Args:
        graph: Graph with Adaptagrams coordinates.
        routes: Edge paths to include in the bounds.

    Returns:
        The x and y axis bounds as ``(x_min, x_max, y_min, y_max)``.
    """
    coordinates = ag.layout_matrix(graph)
    x_values = list(coordinates[:, 0])
    y_values = list(coordinates[:, 1])
    for route in routes:
        x_values.extend(point[0] for point in route)
        y_values.extend(point[1] for point in route)
    padding = 45.0
    return (
        min(x_values) - padding,
        max(x_values) + padding,
        min(y_values) - padding,
        max(y_values) + padding,
    )


def draw_network(
    graph: ig.Graph,
    routes: list[list[tuple[float, float]]],
    output_path: Path,
    title: str,
) -> None:
    """Draw rectangle nodes and explicit connector paths to a PNG file.

    Args:
        graph: Graph containing Adaptagrams center coordinates.
        routes: One ordered coordinate path per edge.
        output_path: Destination PNG path.
        title: Figure title.
    """
    coordinates = ag.layout_matrix(graph)
    figure, axis = plt.subplots(figsize=(8, 4.5), dpi=150)
    axis: Axes
    figure.patch.set_facecolor("#f8fafc")
    axis.set_facecolor("#f8fafc")

    for route in routes:
        x_values, y_values = zip(*route, strict=True)
        axis.plot(
            x_values,
            y_values,
            color="#64748b",
            linewidth=1.35,
            solid_capstyle="round",
            solid_joinstyle="round",
            zorder=1,
        )

    for index, (x_value, y_value) in enumerate(coordinates):
        node = Rectangle(
            (x_value - NODE_WIDTH / 2, y_value - NODE_HEIGHT / 2),
            NODE_WIDTH,
            NODE_HEIGHT,
            facecolor="#eff6ff",
            edgecolor="#2563eb",
            linewidth=1.5,
            zorder=2,
        )
        axis.add_patch(node)
        axis.text(
            x_value,
            y_value,
            graph.vs[index]["name"],
            ha="center",
            va="center",
            color="#0f172a",
            fontsize=8,
            fontweight="bold",
            zorder=3,
        )

    x_min, x_max, y_min, y_max = drawing_bounds(graph, routes)
    axis.set_xlim(x_min, x_max)
    axis.set_ylim(y_max, y_min)
    axis.set_aspect("equal", adjustable="box")
    axis.set_title(title, color="#0f172a", fontsize=12, pad=10)
    axis.axis("off")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)


def main() -> None:
    """Generate matching before-and-after PNG images."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("docs/images"),
        help="directory for the generated PNG files",
    )
    args = parser.parse_args()

    graph = random_network()
    laid_out = ag.layout_graph(graph, ideal_edge_length=85.0)
    coordinates = ag.layout_matrix(laid_out)
    straight_routes = [
        [tuple(coordinates[source]), tuple(coordinates[target])]
        for source, target in laid_out.get_edgelist()
    ]
    routed = ag.route_edges(
        laid_out,
        routing="orthogonal",
        routing_parameters={
            "shape_buffer_distance": 6.0,
            "ideal_nudging_distance": 8.0,
        },
    )

    draw_network(
        laid_out,
        straight_routes,
        args.output_dir / "random-network-before.png",
        "Before: straight center-to-center edges",
    )
    draw_network(
        routed,
        routed.es["adaptagrams_route"],
        args.output_dir / "random-network-after.png",
        "After: libavoid orthogonal routing",
    )
    print(f"Wrote PNG images to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
