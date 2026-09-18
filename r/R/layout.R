#' Lay out a graph using libcola
#'
#' @param graph_or_vertices An igraph graph or ordinary vertex records.
#' @param edges Ordinary one-based edge records; omitted for igraph input.
#' @param coordinate_attributes Optional initial coordinate names.
#' @param width_attribute,height_attribute Vertex dimension attributes.
#' @param default_width,default_height Defaults for absent dimensions.
#' @param output_attributes Computed coordinate attribute names.
#' @param overwrite Also replace x and y when true.
#' @param ideal_edge_length Positive libcola ideal edge length.
#' @param avoid_node_overlaps Whether to generate non-overlap constraints.
#' @param max_iterations Solver iteration limit.
#'
#' @return An igraph graph or structured ordinary result.
#' @export
layout_graph <- function(
    graph_or_vertices,
    edges = NULL,
    coordinate_attributes = NULL,
    width_attribute = "width",
    height_attribute = "height",
    default_width = .default_width,
    default_height = .default_height,
    output_attributes = c("adaptagrams_x", "adaptagrams_y"),
    overwrite = FALSE,
    ideal_edge_length = 100,
    avoid_node_overlaps = TRUE,
    max_iterations = 100L
) {
    normalized <- .normalize_input(
        graph_or_vertices,
        edges,
        FALSE,
        coordinate_attributes,
        width_attribute,
        height_attribute,
        default_width,
        default_height,
        ideal_edge_length
    )
    coordinates <- .native_layout(
        normalized$rectangles,
        normalized$edges,
        ideal_edge_length,
        avoid_node_overlaps,
        max_iterations
    )
    .apply_coordinates(normalized, coordinates, output_attributes, overwrite)
}

#' Remove rectangular node overlaps using libcola and libvpsc
#'
#' @inheritParams layout_graph
#' @return An igraph graph or structured ordinary result.
#' @export
avoid_overlaps <- function(
    graph_or_vertices,
    edges = NULL,
    coordinate_attributes = NULL,
    width_attribute = "width",
    height_attribute = "height",
    default_width = .default_width,
    default_height = .default_height,
    output_attributes = c("adaptagrams_x", "adaptagrams_y"),
    overwrite = FALSE,
    max_iterations = 100L
) {
    normalized <- .normalize_input(
        graph_or_vertices,
        edges,
        TRUE,
        coordinate_attributes,
        width_attribute,
        height_attribute,
        default_width,
        default_height,
        100
    )
    coordinates <- .native_avoid_overlaps(
        normalized$rectangles,
        max_iterations
    )
    .apply_coordinates(normalized, coordinates, output_attributes, overwrite)
}

#' Lay out and route a graph
#'
#' @inheritParams layout_graph
#' @param routing Either `"orthogonal"` or `"polyline"`.
#' @param routing_parameters Named libavoid parameter list.
#' @return An igraph graph or structured ordinary result.
#' @export
layout_and_route <- function(
    graph_or_vertices,
    edges = NULL,
    routing = c("orthogonal", "polyline"),
    coordinate_attributes = NULL,
    width_attribute = "width",
    height_attribute = "height",
    default_width = .default_width,
    default_height = .default_height,
    output_attributes = c("adaptagrams_x", "adaptagrams_y"),
    overwrite = FALSE,
    ideal_edge_length = 100,
    avoid_node_overlaps = TRUE,
    max_iterations = 100L,
    routing_parameters = list()
) {
    routing <- match.arg(routing)
    laid_out <- layout_graph(
        graph_or_vertices,
        edges,
        coordinate_attributes,
        width_attribute,
        height_attribute,
        default_width,
        default_height,
        output_attributes,
        overwrite,
        ideal_edge_length,
        avoid_node_overlaps,
        max_iterations
    )
    if (.is_graph(laid_out)) {
        return(route_edges(
            laid_out,
            routing = routing,
            coordinate_attributes = output_attributes,
            width_attribute = width_attribute,
            height_attribute = height_attribute,
            default_width = default_width,
            default_height = default_height,
            routing_parameters = routing_parameters
        ))
    }
    route_edges(
        laid_out$vertices,
        laid_out$edges,
        routing,
        output_attributes,
        width_attribute,
        height_attribute,
        default_width,
        default_height,
        routing_parameters = routing_parameters
    )
}

#' Extract an N-by-2 coordinate matrix in vertex order
#'
#' @param graph_or_result An igraph graph or structured result.
#' @return A numeric matrix usable as the `layout` argument to plot.igraph.
#' @export
layout_matrix <- function(graph_or_result) {
    if (.is_graph(graph_or_result)) {
        names <- igraph::vertex_attr_names(graph_or_result)
        coordinate_names <- if (all(
            c("adaptagrams_x", "adaptagrams_y") %in% names
        )) {
            c("adaptagrams_x", "adaptagrams_y")
        } else if (all(c("x", "y") %in% names)) {
            c("x", "y")
        } else {
            stop("graph has no complete coordinate pair", call. = FALSE)
        }
        return(cbind(
            igraph::vertex_attr(graph_or_result, coordinate_names[[1]]),
            igraph::vertex_attr(graph_or_result, coordinate_names[[2]])
        ))
    }
    if (is.list(graph_or_result) && !is.null(graph_or_result$coordinates)) {
        return(as.matrix(graph_or_result$coordinates))
    }
    stop("expected an igraph graph or Adaptagrams result", call. = FALSE)
}

#' Extract routed connectors in edge order
#'
#' @param graph_or_result An igraph graph or structured routing result.
#' @return A data frame with an edge-level list column of two-column matrices.
#' @export
get_edge_routes <- function(graph_or_result) {
    if (.is_graph(graph_or_result)) {
        if (!("adaptagrams_route" %in%
                igraph::edge_attr_names(graph_or_result))) {
            stop("graph has no adaptagrams_route attribute", call. = FALSE)
        }
        endpoints <- igraph::as_edgelist(graph_or_result, names = FALSE)
        return(data.frame(
            edge_index = seq_len(igraph::ecount(graph_or_result)) - 1L,
            source = endpoints[, 1],
            target = endpoints[, 2],
            route = I(igraph::edge_attr(
                graph_or_result,
                "adaptagrams_route"
            ))
        ))
    }
    if (is.list(graph_or_result) && !is.null(graph_or_result$routes)) {
        return(data.frame(
            edge_index = seq_along(graph_or_result$routes) - 1L,
            source = graph_or_result$edges$source,
            target = graph_or_result$edges$target,
            route = I(graph_or_result$routes)
        ))
    }
    stop("expected an igraph graph or Adaptagrams result", call. = FALSE)
}
