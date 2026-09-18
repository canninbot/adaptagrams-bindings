test_that("required native igraph routing example works", {
    graph <- obstacle_graph()
    routed <- route_edges(graph, routing = "orthogonal")
    expect_true(igraph::is_igraph(routed))
    expect_equal(igraph::vcount(routed), igraph::vcount(graph))
    expect_equal(igraph::ecount(routed), igraph::ecount(graph))
    routes <- igraph::edge_attr(routed, "adaptagrams_route")
    expect_route_avoids(routes[[1]], c(100, 0), c(40, 40))
})

test_that("orthogonal and polyline routing avoid obstacles", {
    orthogonal <- igraph::edge_attr(
        route_edges(obstacle_graph(), routing = "orthogonal"),
        "adaptagrams_route"
    )[[1]]
    differences <- apply(orthogonal, 2, diff)
    expect_true(all(abs(differences[, 1]) < 1e-9 |
        abs(differences[, 2]) < 1e-9))

    polyline <- igraph::edge_attr(
        route_edges(obstacle_graph(), routing = "polyline"),
        "adaptagrams_route"
    )[[1]]
    expect_true(all(is.finite(polyline)))
    expect_route_avoids(polyline, c(100, 0), c(40, 40))
})

test_that("parallel edges preserve edge identity", {
    graph <- igraph::make_empty_graph(2, directed = TRUE)
    graph <- igraph::add_edges(graph, c(1, 2, 1, 2))
    graph <- igraph::set_vertex_attr(graph, "x", value = c(0, 100))
    graph <- igraph::set_vertex_attr(graph, "y", value = c(0, 0))
    graph <- igraph::set_edge_attr(
        graph,
        "edge_id",
        value = c("first", "second")
    )
    result <- route_edges(graph)
    expect_equal(igraph::ecount(result), 2)
    expect_equal(
        igraph::edge_attr(result, "edge_id"),
        c("first", "second")
    )
    expect_length(igraph::edge_attr(result, "adaptagrams_route"), 2)
})

test_that("self loops produce an edge-specific error", {
    graph <- igraph::make_empty_graph(1, directed = TRUE)
    graph <- igraph::add_edges(graph, c(1, 1))
    graph <- igraph::set_vertex_attr(graph, "x", value = 0)
    graph <- igraph::set_vertex_attr(graph, "y", value = 0)
    expect_error(route_edges(graph), "edge 0 is a self-loop")
    expect_equal(igraph::ecount(graph), 1)
})

test_that("ordinary data frames use the native router", {
    vertices <- data.frame(
        x = c(0, 200, 100),
        y = c(0, 0, 0),
        width = c(80, 80, 40),
        height = c(40, 40, 40)
    )
    edges <- data.frame(source = 1L, target = 2L)
    result <- route_edges(vertices, edges)
    expect_length(result$routes, 1)
    expect_equal(result$edges$adaptagrams_edge_id, "edge-0")
    expect_route_avoids(result$routes[[1]], c(100, 0), c(40, 40))
})

test_that("fixed ports and direction constraints are supported", {
    graph <- obstacle_graph()
    graph <- igraph::set_edge_attr(
        graph,
        "source_port",
        value = list(c(40, 0))
    )
    graph <- igraph::set_edge_attr(
        graph,
        "target_port",
        value = list(c(160, 0))
    )
    graph <- igraph::set_edge_attr(graph, "source_direction", value = "right")
    graph <- igraph::set_edge_attr(graph, "target_direction", value = "left")
    result <- route_edges(
        graph,
        source_port_attribute = "source_port",
        target_port_attribute = "target_port",
        source_direction_attribute = "source_direction",
        target_direction_attribute = "target_direction",
        routing_parameters = list(shape_buffer_distance = 2)
    )
    route <- igraph::edge_attr(result, "adaptagrams_route")[[1]]
    expect_equal(unname(route[1, ]), c(40, 0))
    expect_equal(unname(route[nrow(route), ]), c(160, 0))
})
