# Generated manually for the small stable native surface.

.native_route <- function(
    rectangles,
    edges,
    routing,
    parameters,
    source_points,
    target_points,
    source_directions,
    target_directions
) {
    .Call(
        `_adaptagrams_native_route`,
        rectangles,
        edges,
        routing,
        parameters,
        source_points,
        target_points,
        source_directions,
        target_directions
    )
}

.native_layout <- function(
    rectangles,
    edges,
    ideal_edge_length,
    avoid_node_overlaps,
    max_iterations
) {
    .Call(
        `_adaptagrams_native_layout`,
        rectangles,
        edges,
        ideal_edge_length,
        avoid_node_overlaps,
        max_iterations
    )
}

.native_avoid_overlaps <- function(rectangles, max_iterations) {
    .Call(`_adaptagrams_native_avoid_overlaps`, rectangles, max_iterations)
}
