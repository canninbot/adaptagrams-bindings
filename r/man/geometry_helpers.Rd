\name{geometry_helpers}
\alias{layout_matrix}
\alias{get_edge_routes}
\title{Extract computed Adaptagrams geometry}
\usage{
layout_matrix(graph_or_result)

get_edge_routes(graph_or_result)
}
\description{
Returns coordinates in vertex order or routes in edge order using ordinary R
matrices and data frames.
}
\arguments{
\item{graph_or_result}{An igraph graph or structured Adaptagrams result.}
}
\value{A numeric coordinate matrix or an edge-indexed route data frame.}
