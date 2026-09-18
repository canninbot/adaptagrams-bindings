\name{route_edges}
\alias{route_edges}
\title{Route graph edges around rectangular obstacles}
\usage{
route_edges(graph_or_vertices, edges = NULL,
  routing = c("orthogonal", "polyline"), coordinate_attributes = NULL,
  width_attribute = "width", height_attribute = "height",
  default_width = .default_width, default_height = .default_height,
  route_attribute = "adaptagrams_route", source_port_attribute = NULL,
  target_port_attribute = NULL, source_direction_attribute = NULL,
  target_direction_attribute = NULL, routing_parameters = list())
}
\description{
Calls libavoid and returns an igraph graph with an edge-level list attribute of
two-column route matrices. Ordinary data frames and lists are also accepted.
}
\arguments{
\item{graph_or_vertices}{An igraph graph or ordinary vertex records.}
\item{edges}{One-based ordinary edge records, or NULL for igraph input.}
\item{routing}{Orthogonal or polyline routing.}
\item{coordinate_attributes}{Optional pair of coordinate names.}
\item{width_attribute, height_attribute}{Vertex dimension names.}
\item{default_width, default_height}{Defaults for absent dimensions.}
\item{route_attribute}{Output edge route attribute.}
\item{source_port_attribute, target_port_attribute}{Optional fixed-port edge attributes.}
\item{source_direction_attribute, target_direction_attribute}{Optional direction edge attributes.}
\item{routing_parameters}{Named list of libavoid parameters.}
}
\value{An igraph graph or structured ordinary result.}
