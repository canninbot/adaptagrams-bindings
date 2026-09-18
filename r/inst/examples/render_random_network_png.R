# Render a random igraph network before and after orthogonal routing.

suppressPackageStartupMessages({
    library(igraph)
    library(adaptagrams)
})

node_count <- 14L
random_seed <- 20260918L
extra_edge_count <- 12L
node_width <- 46
node_height <- 30

# Create a reproducible connected random graph with rectangular nodes.
random_network <- function() {
    set.seed(random_seed)
    graph <- igraph::make_ring(node_count)
    candidates <- t(utils::combn(seq_len(node_count), 2L))
    ring_edges <- rbind(
        cbind(seq_len(node_count - 1L), seq.int(2L, node_count)),
        c(node_count, 1L)
    )
    edge_key <- function(edges) {
        paste(pmin(edges[, 1], edges[, 2]), pmax(edges[, 1], edges[, 2]))
    }
    candidates <- candidates[!(edge_key(candidates) %in% edge_key(ring_edges)), ]
    additions <- candidates[
        sample.int(nrow(candidates), extra_edge_count),
        ,
        drop = FALSE
    ]
    graph <- igraph::add_edges(graph, as.vector(t(additions)))
    graph <- igraph::set_vertex_attr(
        graph,
        "name",
        value = as.character(seq_len(node_count))
    )
    graph <- igraph::set_vertex_attr(
        graph,
        "width",
        value = rep(node_width, node_count)
    )
    igraph::set_vertex_attr(
        graph,
        "height",
        value = rep(node_height, node_count)
    )
}

# Draw the node rectangles and explicit edge paths to one PNG file.
draw_network <- function(graph, routes, output_path, title) {
    coordinates <- layout_matrix(graph)
    route_points <- do.call(rbind, routes)
    x_range <- range(c(coordinates[, 1], route_points[, 1])) + c(-45, 45)
    y_range <- range(c(coordinates[, 2], route_points[, 2])) + c(-45, 45)

    grDevices::png(output_path, width = 1200, height = 675, res = 150)
    on.exit(grDevices::dev.off())
    graphics::par(mar = c(0.5, 0.5, 2.5, 0.5), bg = "#f8fafc")
    graphics::plot.new()
    graphics::plot.window(xlim = x_range, ylim = rev(y_range), asp = 1)
    for (route in routes) {
        graphics::lines(
            route[, 1],
            route[, 2],
            col = "#64748b",
            lwd = 1.5,
            lend = "round",
            ljoin = "round"
        )
    }
    graphics::rect(
        coordinates[, 1] - node_width / 2,
        coordinates[, 2] - node_height / 2,
        coordinates[, 1] + node_width / 2,
        coordinates[, 2] + node_height / 2,
        col = "#eff6ff",
        border = "#2563eb",
        lwd = 1.5
    )
    graphics::text(
        coordinates[, 1],
        coordinates[, 2],
        labels = igraph::vertex_attr(graph, "name"),
        col = "#0f172a",
        cex = 0.8,
        font = 2
    )
    graphics::title(main = title, col.main = "#0f172a", cex.main = 1.1)
}

# Generate matching before-and-after images in the requested directory.
main <- function() {
    arguments <- commandArgs(trailingOnly = TRUE)
    output_dir <- if (length(arguments)) arguments[[1]] else "docs/images"
    dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

    graph <- random_network()
    laid_out <- layout_graph(graph, ideal_edge_length = 85)
    coordinates <- layout_matrix(laid_out)
    endpoints <- igraph::as_edgelist(laid_out, names = FALSE)
    straight_routes <- lapply(seq_len(nrow(endpoints)), function(index) {
        coordinates[endpoints[index, ], , drop = FALSE]
    })
    routed <- route_edges(
        laid_out,
        routing = "orthogonal",
        routing_parameters = list(
            shape_buffer_distance = 6,
            ideal_nudging_distance = 8
        )
    )

    draw_network(
        laid_out,
        straight_routes,
        file.path(output_dir, "r-random-network-before.png"),
        "Before: straight center-to-center edges"
    )
    draw_network(
        routed,
        igraph::edge_attr(routed, "adaptagrams_route"),
        file.path(output_dir, "r-random-network-after.png"),
        "After: libavoid orthogonal routing"
    )
    message("Wrote PNG images to ", normalizePath(output_dir))
}

if (sys.nframe() == 0L) {
    main()
}
