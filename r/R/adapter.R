.default_width <- 40
.default_height <- 30

.is_graph <- function(value) {
    igraph::is_igraph(value)
}

.records <- function(value, label) {
    if (is.data.frame(value)) {
        return(value)
    }
    if (is.matrix(value)) {
        return(as.data.frame(value, stringsAsFactors = FALSE))
    }
    if (is.list(value)) {
        if (length(value) == 0) {
            return(data.frame())
        }
        return(do.call(rbind.data.frame, c(value, stringsAsFactors = FALSE)))
    }
    stop(label, " must be a data frame, matrix, or list", call. = FALSE)
}

.validate_numeric <- function(value, description, positive = FALSE) {
    if (!is.numeric(value) || length(value) != 1 || !is.finite(value)) {
        stop(description, " must be a finite number", call. = FALSE)
    }
    if (positive && value <= 0) {
        stop(description, " must be positive", call. = FALSE)
    }
    as.numeric(value)
}

.direction_flags <- function(value, description) {
    if (is.null(value) || length(value) == 0 || is.na(value)) {
        return(15L)
    }
    if (is.numeric(value) && length(value) == 1 &&
            value >= 0 && value <= 15) {
        return(as.integer(value))
    }
    if (!is.character(value) || length(value) != 1) {
        stop(description, " must be direction names or an integer 0..15")
    }
    mapping <- c(none = 0L, up = 1L, down = 2L, left = 4L, right = 8L, all = 15L)
    parts <- trimws(strsplit(tolower(value), "[|,]")[[1]])
    if (any(!(parts %in% names(mapping)))) {
        stop(description, " contains an unknown direction", call. = FALSE)
    }
    Reduce(bitwOr, unname(mapping[parts]), init = 0L)
}

.edge_routing_options <- function(
    normalized,
    source_port_attribute,
    target_port_attribute,
    source_direction_attribute,
    target_direction_attribute
) {
    count <- nrow(normalized$edges)
    values <- function(attribute) {
        if (is.null(attribute)) {
            return(rep(list(NULL), count))
        }
        if (normalized$is_graph) {
            if (!(attribute %in% igraph::edge_attr_names(normalized$graph))) {
                stop("edge attribute ", attribute, " is missing", call. = FALSE)
            }
            return(as.list(igraph::edge_attr(normalized$graph, attribute)))
        }
        if (!(attribute %in% names(normalized$edge_records))) {
            stop("edge field ", attribute, " is missing", call. = FALSE)
        }
        as.list(normalized$edge_records[[attribute]])
    }
    point_matrix <- function(items, description) {
        result <- matrix(NA_real_, nrow = count, ncol = 2)
        for (index in seq_len(count)) {
            item <- items[[index]]
            if (!is.null(item)) {
                item <- as.numeric(item)
                if (length(item) != 2 || any(!is.finite(item))) {
                    stop(description, " must contain finite coordinate pairs")
                }
                result[index, ] <- item
            }
        }
        result
    }
    source_directions <- values(source_direction_attribute)
    target_directions <- values(target_direction_attribute)
    list(
        source_points = point_matrix(
            values(source_port_attribute),
            "source ports"
        ),
        target_points = point_matrix(
            values(target_port_attribute),
            "target ports"
        ),
        source_directions = vapply(
            seq_len(count),
            function(index) .direction_flags(
                source_directions[[index]],
                paste("edge", index - 1, "source direction")
            ),
            integer(1)
        ),
        target_directions = vapply(
            seq_len(count),
            function(index) .direction_flags(
                target_directions[[index]],
                paste("edge", index - 1, "target direction")
            ),
            integer(1)
        )
    )
}

.coordinate_names <- function(names, coordinate_attributes, allow_missing) {
    if (!is.null(coordinate_attributes)) {
        if (length(coordinate_attributes) != 2 ||
                !all(coordinate_attributes %in% names)) {
            stop(
                "explicit coordinate attributes must both be present",
                call. = FALSE
            )
        }
        return(coordinate_attributes)
    }
    for (candidate in list(
        c("adaptagrams_x", "adaptagrams_y"),
        c("x", "y")
    )) {
        present <- candidate %in% names
        if (all(present)) {
            return(candidate)
        }
        if (any(present)) {
            stop(
                "coordinate attributes ",
                paste(candidate, collapse = " and "),
                " must both be present",
                call. = FALSE
            )
        }
    }
    if (allow_missing) {
        return(NULL)
    }
    stop(
        "routing requires adaptagrams_x/adaptagrams_y or x/y attributes",
        call. = FALSE
    )
}

.initial_coordinates <- function(count, ideal_edge_length) {
    if (count == 0) {
        return(matrix(numeric(), ncol = 2))
    }
    if (count == 1) {
        return(matrix(c(0, 0), ncol = 2))
    }
    radius <- max(
        ideal_edge_length,
        ideal_edge_length * count / (2 * pi)
    )
    angles <- 2 * pi * (seq_len(count) - 1) / count
    cbind(radius * cos(angles), radius * sin(angles))
}

.normalize_input <- function(
    graph_or_vertices,
    edges,
    require_coordinates,
    coordinate_attributes,
    width_attribute,
    height_attribute,
    default_width,
    default_height,
    ideal_edge_length
) {
    is_graph <- .is_graph(graph_or_vertices)
    if (is_graph) {
        if (!is.null(edges)) {
            stop("edges must not be supplied with igraph input", call. = FALSE)
        }
        graph <- graph_or_vertices
        vertex_names <- igraph::vertex_attr_names(graph)
        coordinate_names <- .coordinate_names(
            vertex_names,
            coordinate_attributes,
            !require_coordinates
        )
        if (is.null(coordinate_names)) {
            coordinates <- .initial_coordinates(
                igraph::vcount(graph),
                ideal_edge_length
            )
        } else {
            coordinates <- cbind(
                igraph::vertex_attr(graph, coordinate_names[[1]]),
                igraph::vertex_attr(graph, coordinate_names[[2]])
            )
        }
        widths <- if (width_attribute %in% vertex_names) {
            igraph::vertex_attr(graph, width_attribute)
        } else {
            rep(default_width, igraph::vcount(graph))
        }
        heights <- if (height_attribute %in% vertex_names) {
            igraph::vertex_attr(graph, height_attribute)
        } else {
            rep(default_height, igraph::vcount(graph))
        }
        edge_matrix <- igraph::as_edgelist(graph, names = FALSE)
        if (length(edge_matrix) == 0) {
            edge_matrix <- matrix(integer(), ncol = 2)
        }
        edge_matrix <- matrix(
            as.integer(edge_matrix) - 1L,
            ncol = 2
        )
        vertex_records <- NULL
        edge_records <- NULL
    } else {
        if (is.null(edges)) {
            stop("ordinary vertex input requires edges", call. = FALSE)
        }
        vertex_records <- .records(graph_or_vertices, "vertices")
        edge_records <- .records(edges, "edges")
        coordinate_names <- .coordinate_names(
            names(vertex_records),
            coordinate_attributes,
            !require_coordinates
        )
        if (is.null(coordinate_names)) {
            coordinates <- .initial_coordinates(
                nrow(vertex_records),
                ideal_edge_length
            )
        } else {
            coordinates <- as.matrix(vertex_records[coordinate_names])
        }
        widths <- if (width_attribute %in% names(vertex_records)) {
            vertex_records[[width_attribute]]
        } else {
            rep(default_width, nrow(vertex_records))
        }
        heights <- if (height_attribute %in% names(vertex_records)) {
            vertex_records[[height_attribute]]
        } else {
            rep(default_height, nrow(vertex_records))
        }
        if (!all(c("source", "target") %in% names(edge_records))) {
            stop("ordinary edges require source and target columns", call. = FALSE)
        }
        edge_matrix <- cbind(edge_records$source, edge_records$target) - 1L
        storage.mode(edge_matrix) <- "integer"
    }
    if (nrow(coordinates) != length(widths) ||
            nrow(coordinates) != length(heights)) {
        stop("inconsistent vertex geometry lengths", call. = FALSE)
    }
    numeric_coordinates <- suppressWarnings(matrix(
        as.numeric(coordinates),
        nrow = nrow(coordinates),
        ncol = 2
    ))
    numeric_widths <- suppressWarnings(as.numeric(widths))
    numeric_heights <- suppressWarnings(as.numeric(heights))
    if (any(!is.finite(numeric_coordinates))) {
        stop("vertex coordinates must be finite numeric values", call. = FALSE)
    }
    if (any(!is.finite(numeric_widths)) || any(numeric_widths <= 0)) {
        stop("vertex widths must be finite and positive", call. = FALSE)
    }
    if (any(!is.finite(numeric_heights)) || any(numeric_heights <= 0)) {
        stop("vertex heights must be finite and positive", call. = FALSE)
    }
    vertex_count <- nrow(numeric_coordinates)
    if (length(edge_matrix) > 0 &&
            (any(edge_matrix < 0) || any(edge_matrix >= vertex_count))) {
        stop("edge references an invalid vertex index", call. = FALSE)
    }
    if (require_coordinates && nrow(edge_matrix) > 0) {
        loops <- which(edge_matrix[, 1] == edge_matrix[, 2])
        if (length(loops) > 0) {
            stop(
                "edge ",
                loops[[1]] - 1,
                " is a self-loop; libavoid self-loop routing is unsupported",
                call. = FALSE
            )
        }
    }
    list(
        graph = if (is_graph) graph_or_vertices else NULL,
        is_graph = is_graph,
        rectangles = cbind(
            numeric_coordinates,
            numeric_widths,
            numeric_heights
        ),
        edges = edge_matrix,
        vertices = vertex_records,
        edge_records = edge_records
    )
}

.apply_coordinates <- function(
    normalized,
    coordinates,
    output_attributes,
    overwrite
) {
    if (normalized$is_graph) {
        graph <- normalized$graph
        existing <- igraph::vertex_attr_names(graph)
        if (any(output_attributes %in% existing)) {
            stop("output coordinate attribute already exists", call. = FALSE)
        }
        graph <- igraph::set_vertex_attr(
            graph,
            output_attributes[[1]],
            value = coordinates[, 1]
        )
        graph <- igraph::set_vertex_attr(
            graph,
            output_attributes[[2]],
            value = coordinates[, 2]
        )
        if (overwrite) {
            graph <- igraph::set_vertex_attr(graph, "x", value = coordinates[, 1])
            graph <- igraph::set_vertex_attr(graph, "y", value = coordinates[, 2])
        }
        return(graph)
    }
    vertices <- normalized$vertices
    vertices[[output_attributes[[1]]]] <- coordinates[, 1]
    vertices[[output_attributes[[2]]]] <- coordinates[, 2]
    if (overwrite) {
        vertices$x <- coordinates[, 1]
        vertices$y <- coordinates[, 2]
    }
    list(
        vertices = vertices,
        edges = normalized$edge_records,
        coordinates = coordinates
    )
}
