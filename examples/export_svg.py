"""Export actual Adaptagrams node and connector geometry as SVG."""

import argparse
from html import escape
from pathlib import Path

import igraph as ig
import pyadaptagrams as ag


def svg_document(graph: ig.Graph) -> str:
    """Create an SVG using graph rectangles and routed polylines.

    Args:
        graph: A routed graph with center coordinates.

    Returns:
        A complete SVG document string.
    """
    coordinates = ag.layout_matrix(graph)
    routes = graph.es["adaptagrams_route"]
    widths = (
        graph.vs["width"] if "width" in graph.vs.attributes() else [40] * graph.vcount()
    )
    heights = (
        graph.vs["height"]
        if "height" in graph.vs.attributes()
        else [30] * graph.vcount()
    )
    labels = (
        graph.vs["name"]
        if "name" in graph.vs.attributes()
        else list(range(graph.vcount()))
    )
    parts = [
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="-150 -150 300 300">""",
        """<g fill="none" stroke="#334155" stroke-width="2">""",
    ]
    for route in routes:
        points = " ".join(f"{x},{y}" for x, y in route)
        parts.append(f'<polyline points="{points}" />')
    parts.append("</g>")
    for index, (x, y) in enumerate(coordinates):
        parts.append(
            f'<rect x="{x - widths[index] / 2}" y="{y - heights[index] / 2}" '
            f'width="{widths[index]}" height="{heights[index]}" '
            'fill="white" stroke="#0f172a" />'
        )
        parts.append(
            f'<text x="{x}" y="{y}" text-anchor="middle" '
            f'dominant-baseline="middle">{escape(str(labels[index]))}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    """Build the example graph and write an SVG."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, default=Path("adaptagrams.svg"))
    args = parser.parse_args()
    graph = ig.Graph.Ring(5)
    graph.vs["name"] = list("ABCDE")
    result = ag.layout_and_route(graph)
    args.output.write_text(svg_document(result), encoding="utf-8")


if __name__ == "__main__":
    main()
