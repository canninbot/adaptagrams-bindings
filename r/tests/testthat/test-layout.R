test_that("required ring layout example works", {
    graph <- igraph::make_ring(5)
    result <- layout_and_route(graph, routing = "orthogonal")
    expect_true(igraph::is_igraph(result))
    expect_equal(dim(layout_matrix(result)), c(5, 2))
    expect_equal(nrow(get_edge_routes(result)), 5)
})

test_that("layout and overlap removal return native igraph graphs", {
    graph <- igraph::make_empty_graph(2)
    graph <- igraph::set_vertex_attr(graph, "x", value = c(0, 0))
    graph <- igraph::set_vertex_attr(graph, "y", value = c(0, 0))
    graph <- igraph::set_vertex_attr(graph, "width", value = c(50, 50))
    graph <- igraph::set_vertex_attr(graph, "height", value = c(30, 30))
    separated <- avoid_overlaps(graph)
    coordinates <- layout_matrix(separated)
    expect_true(abs(diff(coordinates[, 1])) >= 50 - 1e-7 ||
        abs(diff(coordinates[, 2])) >= 30 - 1e-7)
    expect_true(igraph::is_igraph(layout_graph(igraph::make_ring(4))))
})

test_that("empty and isolated vertices survive", {
    empty <- layout_and_route(igraph::make_empty_graph())
    expect_true(igraph::is_igraph(empty))
    expect_equal(igraph::vcount(empty), 0)
    expect_equal(dim(layout_matrix(empty)), c(0, 2))

    graph <- igraph::make_empty_graph(4)
    graph <- igraph::add_edges(graph, c(1, 2))
    result <- layout_and_route(graph)
    expect_equal(igraph::vcount(result), 4)
    expect_true(all(is.finite(layout_matrix(result))))
})

test_that("layout matrix preserves vertex ordering", {
    graph <- igraph::make_ring(5)
    result <- layout_graph(graph)
    coordinates <- layout_matrix(result)
    expect_equal(coordinates[, 1], igraph::vertex_attr(result, "adaptagrams_x"))
    expect_equal(coordinates[, 2], igraph::vertex_attr(result, "adaptagrams_y"))
})
