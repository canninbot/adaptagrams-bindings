"""Compare normalized Python and R route geometry for one fixed fixture."""

import csv
import io
import subprocess
from pathlib import Path

import igraph as ig
import numpy as np
import pyadaptagrams as ag


def main() -> None:
    """Route the same graph in both packages and compare coordinates."""
    graph = ig.Graph(n=3, edges=[(0, 1)], directed=True)
    graph.vs["x"] = [0.0, 200.0, 100.0]
    graph.vs["y"] = [0.0, 0.0, 0.0]
    graph.vs["width"] = [80.0, 80.0, 40.0]
    graph.vs["height"] = [40.0, 40.0, 40.0]
    python_route = np.asarray(
        ag.route_edges(graph).es["adaptagrams_route"][0], dtype=float
    )

    script = Path(__file__).with_name("cross_language_fixture.R")
    completed = subprocess.run(
        ["Rscript", str(script)],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = list(csv.DictReader(io.StringIO(completed.stdout)))
    r_route = np.asarray(
        [(float(row["x"]), float(row["y"])) for row in rows], dtype=float
    )
    np.testing.assert_allclose(python_route, r_route, rtol=1e-9, atol=1e-9)
    print(f"cross-language route matched at {len(rows)} points")


if __name__ == "__main__":
    main()
