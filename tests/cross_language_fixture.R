suppressPackageStartupMessages({
    library(adaptagrams)
    library(igraph)
})

vertices <- data.frame(
    name = c("A", "B", "C"),
    x = c(0, 200, 100),
    y = c(0, 0, 0),
    width = c(80, 80, 40),
    height = c(40, 40, 40)
)
edges <- data.frame(from = "A", to = "B")
graph <- igraph::graph_from_data_frame(edges, TRUE, vertices)
route <- igraph::edge_attr(route_edges(graph), "adaptagrams_route")[[1]]
utils::write.table(
    data.frame(point = seq_len(nrow(route)) - 1L, x = route[, 1], y = route[, 2]),
    file = stdout(),
    sep = ",",
    row.names = FALSE,
    quote = FALSE
)
