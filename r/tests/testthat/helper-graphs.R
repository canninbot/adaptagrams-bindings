obstacle_graph <- function(directed = TRUE) {
    vertices <- data.frame(
        name = c("A", "B", "C"),
        x = c(0, 200, 100),
        y = c(0, 0, 0),
        width = c(80, 80, 40),
        height = c(40, 40, 40),
        color = c("red", "blue", "gray")
    )
    edges <- data.frame(from = "A", to = "B", edge_id = "e1", weight = 2.5)
    graph <- igraph::graph_from_data_frame(edges, directed, vertices)
    igraph::set_graph_attr(graph, "project", "preserved")
}

biological_graph <- function() {
    vertices <- data.frame(
        name = c("A", "R", "B", "C"),
        sbgn_class = c(
            "macromolecule",
            "process",
            "macromolecule",
            "simple chemical"
        ),
        x = c(0, 100, 240, 170),
        y = c(0, 0, 0, 0),
        width = c(60, 20, 60, 50),
        height = c(40, 20, 40, 50),
        compartment = rep("cytosol", 4)
    )
    edges <- data.frame(
        from = c("A", "R"),
        to = c("R", "B"),
        edge_id = c("consumption-1", "production-1"),
        sbgn_arc_class = c("consumption", "production")
    )
    graph <- igraph::graph_from_data_frame(edges, TRUE, vertices)
    igraph::set_graph_attr(graph, "model_id", "reaction-1")
}

graph_snapshot <- function(graph) {
    list(
        vcount = igraph::vcount(graph),
        ecount = igraph::ecount(graph),
        directed = igraph::is_directed(graph),
        endpoints = igraph::as_edgelist(graph, names = FALSE),
        graph_attributes = igraph::graph_attr(graph),
        vertex_attributes = igraph::vertex_attr(graph),
        edge_attributes = igraph::edge_attr(graph)
    )
}

expect_preserved <- function(snapshot, graph) {
    expect_identical(igraph::vcount(graph), snapshot$vcount)
    expect_identical(igraph::ecount(graph), snapshot$ecount)
    expect_identical(igraph::is_directed(graph), snapshot$directed)
    expect_identical(
        igraph::as_edgelist(graph, names = FALSE),
        snapshot$endpoints
    )
    for (name in names(snapshot$graph_attributes)) {
        expect_equal(
            igraph::graph_attr(graph, name),
            snapshot$graph_attributes[[name]]
        )
    }
    for (name in names(snapshot$vertex_attributes)) {
        expect_equal(
            igraph::vertex_attr(graph, name),
            snapshot$vertex_attributes[[name]]
        )
    }
    for (name in names(snapshot$edge_attributes)) {
        expect_equal(
            igraph::edge_attr(graph, name),
            snapshot$edge_attributes[[name]]
        )
    }
}

segment_intersects_interior <- function(first, second, center, size, tol = 1e-9) {
    minimum <- center - size / 2 + tol
    maximum <- center + size / 2 - tol
    delta <- second - first
    lower <- 0
    upper <- 1
    for (dimension in seq_len(2)) {
        if (abs(delta[[dimension]]) <= tol) {
            if (!(minimum[[dimension]] < first[[dimension]] &&
                    first[[dimension]] < maximum[[dimension]])) {
                return(FALSE)
            }
        } else {
            bounds <- c(
                (minimum[[dimension]] - first[[dimension]]) /
                    delta[[dimension]],
                (maximum[[dimension]] - first[[dimension]]) /
                    delta[[dimension]]
            )
            lower <- max(lower, min(bounds))
            upper <- min(upper, max(bounds))
        }
    }
    lower < upper && upper > 0 && lower < 1
}

expect_route_avoids <- function(route, center, size) {
    expect_gte(nrow(route), 2)
    for (index in seq_len(nrow(route) - 1)) {
        expect_false(segment_intersects_interior(
            route[index, ],
            route[index + 1, ],
            center,
            size
        ))
    }
}
