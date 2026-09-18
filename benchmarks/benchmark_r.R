# Reproducible Adaptagrams conversion/layout/routing benchmark.

suppressPackageStartupMessages({
    library(adaptagrams)
    library(igraph)
})

args <- commandArgs(trailingOnly = TRUE)
sizes <- if (length(args)) as.integer(args) else c(10L, 100L, 1000L, 10000L)

benchmark <- function(size) {
    graph <- igraph::make_ring(size)
    circle <- igraph::layout_in_circle(graph)
    graph <- igraph::set_vertex_attr(graph, "x", value = circle[, 1] * size * 10)
    graph <- igraph::set_vertex_attr(graph, "y", value = circle[, 2] * size * 10)
    graph <- igraph::set_vertex_attr(graph, "width", value = rep(20, size))
    graph <- igraph::set_vertex_attr(graph, "height", value = rep(14, size))

    routing <- system.time(route_edges(graph))["elapsed"]
    layout <- system.time(layout_graph(graph))["elapsed"]
    total <- system.time(layout_and_route(graph))["elapsed"]
    data.frame(
        vertices = size,
        edges = igraph::ecount(graph),
        routing_seconds = unname(routing),
        layout_seconds = unname(layout),
        total_seconds = unname(total)
    )
}

cat("R:", R.version.string, "\n")
cat("R igraph:", as.character(utils::packageVersion("igraph")), "\n")
cat("Platform:", R.version$platform, "\n")
print(do.call(rbind, lapply(sizes, benchmark)), row.names = FALSE)
