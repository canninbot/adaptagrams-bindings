#' Route graph edges around rectangular obstacles
#'
#' Coordinates are rectangle centers. For igraph input, computed coordinates
#' are preferred over x/y, vertex and edge order are preserved, and a modified
#' graph copy is returned.
#'
#' @param graph_or_vertices An igraph graph, data frame, matrix, or record list.
#' @param edges Ordinary edge records with one-based source and target columns.
#' @param routing Either `"orthogonal"` or `"polyline"`.
#' @param coordinate_attributes Optional two-item coordinate attribute vector.
#' @param width_attribute,height_attribute Vertex dimension attribute names.
#' @param default_width,default_height Positive defaults for absent dimensions.
#' @param route_attribute Output edge route attribute.
#' @param source_port_attribute,target_port_attribute Optional edge attributes
#'   containing fixed coordinate pairs.
#' @param source_direction_attribute,target_direction_attribute Optional edge
#'   attributes containing direction names (`up`, `down`, `left`, `right`,
#'   `all`) or integer bit flags.
#' @param routing_parameters Named list of supported libavoid parameters.
#'
#' @return An igraph graph, or a structured list for ordinary input.
#' @export
route_edges <- function(
    graph_or_vertices,
    edges = NULL,
    routing = c("orthogonal", "polyline"),
    coordinate_attributes = NULL,
    width_attribute = "width",
    height_attribute = "height",
    default_width = .default_width,
    default_height = .default_height,
    route_attribute = "adaptagrams_route",
    source_port_attribute = NULL,
    target_port_attribute = NULL,
    source_direction_attribute = NULL,
    target_direction_attribute = NULL,
    routing_parameters = list()
) {
    routing <- match.arg(routing)
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
    edge_options <- .edge_routing_options(
        normalized,
        source_port_attribute,
        target_port_attribute,
        source_direction_attribute,
        target_direction_attribute
    )
    routes <- .native_route(
        normalized$rectangles,
        normalized$edges,
        routing,
        routing_parameters,
        edge_options$source_points,
        edge_options$target_points,
        edge_options$source_directions,
        edge_options$target_directions
    )
    if (normalized$is_graph) {
        if (route_attribute %in% igraph::edge_attr_names(normalized$graph) &&
                route_attribute != "adaptagrams_route") {
            stop("output route attribute already exists", call. = FALSE)
        }
        graph <- igraph::set_edge_attr(
            normalized$graph,
            route_attribute,
            value = routes
        )
        edge_names <- igraph::edge_attr_names(graph)
        if (!("edge_id" %in% edge_names) &&
                !("adaptagrams_edge_id" %in% edge_names)) {
            graph <- igraph::set_edge_attr(
                graph,
                "adaptagrams_edge_id",
                value = paste0("edge-", seq_len(igraph::ecount(graph)) - 1L)
            )
        }
        return(graph)
    }
    edge_records <- normalized$edge_records
    if (!("edge_id" %in% names(edge_records))) {
        edge_records$adaptagrams_edge_id <- paste0(
            "edge-",
            seq_len(nrow(edge_records)) - 1L
        )
    }
    edge_records[[route_attribute]] <- I(routes)
    list(
        vertices = normalized$vertices,
        edges = edge_records,
        routes = routes
    )
}
