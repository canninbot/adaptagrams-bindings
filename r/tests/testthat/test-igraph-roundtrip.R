test_that("topology and arbitrary attributes survive round trips", {
    for (directed in c(TRUE, FALSE)) {
        graph <- igraph::make_empty_graph(4, directed = directed)
        graph <- igraph::add_edges(graph, c(1, 2, 1, 2, 3, 2))
        graph <- igraph::set_graph_attr(graph, "label", "network")
        graph <- igraph::set_vertex_attr(
            graph,
            "name",
            value = c("duplicate", "duplicate", "C", "isolated")
        )
        graph <- igraph::set_vertex_attr(
            graph,
            "x",
            value = c(0, 100, 50, 200)
        )
        graph <- igraph::set_vertex_attr(
            graph,
            "y",
            value = c(0, 0, 80, 100)
        )
        graph <- igraph::set_edge_attr(
            graph,
            "label",
            value = c("a", "b", "c")
        )
        before <- graph_snapshot(graph)
        result <- layout_and_route(graph)
        expect_preserved(before, result)
    }
})

test_that("input remains unchanged and missing names are supported", {
    graph <- obstacle_graph()
    before <- graph_snapshot(graph)
    invisible(route_edges(graph))
    expect_equal(graph_snapshot(graph), before)

    unnamed <- igraph::make_empty_graph(2)
    unnamed <- igraph::add_edges(unnamed, c(1, 2))
    unnamed <- igraph::set_vertex_attr(unnamed, "x", value = c(0, 100))
    unnamed <- igraph::set_vertex_attr(unnamed, "y", value = c(0, 0))
    expect_true(igraph::is_igraph(route_edges(unnamed)))
})

test_that("invalid geometry has informative errors", {
    graph <- obstacle_graph()
    graph <- igraph::set_vertex_attr(graph, "width", value = c(80, -1, 40))
    expect_error(route_edges(graph), "widths must be finite and positive")
    graph <- obstacle_graph()
    graph <- igraph::set_vertex_attr(graph, "x", value = c(0, NaN, 100))
    expect_error(route_edges(graph), "coordinates must be finite")
})

test_that("computed coordinates are preferred and output is reusable", {
    graph <- obstacle_graph()
    graph <- igraph::set_vertex_attr(
        graph,
        "adaptagrams_x",
        value = c(0, 200, 100)
    )
    graph <- igraph::set_vertex_attr(
        graph,
        "adaptagrams_y",
        value = c(0, 0, 0)
    )
    once <- route_edges(graph)
    twice <- route_edges(once)
    expect_equal(igraph::as_edgelist(twice), igraph::as_edgelist(graph))
})

test_that("biological graph preserves SBGN metadata and geometry", {
    graph <- biological_graph()
    before <- graph_snapshot(graph)
    result <- route_edges(graph)
    expect_preserved(before, result)
    expect_equal(
        igraph::vertex_attr(result, "sbgn_class")[[2]],
        "process"
    )
    expect_equal(
        igraph::edge_attr(result, "sbgn_arc_class"),
        c("consumption", "production")
    )
    routes <- igraph::edge_attr(result, "adaptagrams_route")
    expect_route_avoids(routes[[2]], c(170, 0), c(50, 50))
})
