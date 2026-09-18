\name{layout_graph}
\alias{layout_graph}
\alias{avoid_overlaps}
\alias{layout_and_route}
\title{Layout and overlap removal}
\description{
Uses libcola and libvpsc to compute center coordinates, optionally followed by
libavoid connector routing.
}
\usage{
layout_graph(graph_or_vertices, edges = NULL, coordinate_attributes = NULL,
  width_attribute = "width", height_attribute = "height",
  default_width = .default_width, default_height = .default_height,
  output_attributes = c("adaptagrams_x", "adaptagrams_y"),
  overwrite = FALSE, ideal_edge_length = 100,
  avoid_node_overlaps = TRUE, max_iterations = 100L)

avoid_overlaps(graph_or_vertices, edges = NULL,
  coordinate_attributes = NULL, width_attribute = "width",
  height_attribute = "height", default_width = .default_width,
  default_height = .default_height,
  output_attributes = c("adaptagrams_x", "adaptagrams_y"),
  overwrite = FALSE, max_iterations = 100L)

layout_and_route(graph_or_vertices, edges = NULL,
  routing = c("orthogonal", "polyline"), coordinate_attributes = NULL,
  width_attribute = "width", height_attribute = "height",
  default_width = .default_width, default_height = .default_height,
  output_attributes = c("adaptagrams_x", "adaptagrams_y"),
  overwrite = FALSE, ideal_edge_length = 100,
  avoid_node_overlaps = TRUE, max_iterations = 100L,
  routing_parameters = list())
}
\arguments{
\item{graph_or_vertices}{An igraph graph or ordinary vertex records.}
\item{edges}{One-based ordinary edge records, or NULL for igraph input.}
\item{routing}{Orthogonal or polyline routing.}
\item{coordinate_attributes}{Optional initial coordinate names.}
\item{width_attribute, height_attribute}{Vertex dimension names.}
\item{default_width, default_height}{Defaults for absent dimensions.}
\item{output_attributes}{Computed coordinate names.}
\item{overwrite}{Whether to also replace x and y.}
\item{ideal_edge_length}{Positive libcola ideal edge length.}
\item{avoid_node_overlaps}{Whether to generate overlap constraints.}
\item{max_iterations}{Solver iteration limit.}
\item{routing_parameters}{Named list of libavoid parameters.}
}
\value{An igraph graph or structured ordinary result.}
