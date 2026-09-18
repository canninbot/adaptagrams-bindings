#include <Rcpp.h>

#include "adaptagrams/adapter.hpp"

namespace {

std::vector<adaptagrams::Rectangle> as_rectangles(
        const Rcpp::NumericMatrix& matrix) {
    if (matrix.ncol() != 4) {
        Rcpp::stop("rectangles must have four columns");
    }
    std::vector<adaptagrams::Rectangle> result;
    result.reserve(matrix.nrow());
    for (int row = 0; row < matrix.nrow(); ++row) {
        result.push_back(
                {matrix(row, 0), matrix(row, 1), matrix(row, 2), matrix(row, 3)});
    }
    return result;
}

std::vector<adaptagrams::Edge> as_edges(const Rcpp::IntegerMatrix& matrix) {
    if (matrix.ncol() != 2) {
        Rcpp::stop("edges must have two columns");
    }
    std::vector<adaptagrams::Edge> result;
    result.reserve(matrix.nrow());
    for (int row = 0; row < matrix.nrow(); ++row) {
        if (matrix(row, 0) < 0 || matrix(row, 1) < 0) {
            Rcpp::stop("edge indices must be nonnegative");
        }
        result.push_back({
                static_cast<std::size_t>(matrix(row, 0)),
                static_cast<std::size_t>(matrix(row, 1))});
    }
    return result;
}

Rcpp::NumericMatrix as_matrix(const std::vector<adaptagrams::Point>& points) {
    Rcpp::NumericMatrix result(points.size(), 2);
    for (std::size_t row = 0; row < points.size(); ++row) {
        result(row, 0) = points[row].x;
        result(row, 1) = points[row].y;
    }
    Rcpp::colnames(result) = Rcpp::CharacterVector::create("x", "y");
    return result;
}

}  // namespace

// [[Rcpp::export]]
SEXP native_route(
        Rcpp::NumericMatrix rectangles,
        Rcpp::IntegerMatrix edges,
        std::string routing,
        Rcpp::List parameters,
        Rcpp::NumericMatrix source_points,
        Rcpp::NumericMatrix target_points,
        Rcpp::IntegerVector source_directions,
        Rcpp::IntegerVector target_directions) {
    adaptagrams::RoutingOptions options;
    options.routing = routing;
    if (parameters.size() > 0) {
        const Rcpp::CharacterVector names = parameters.names();
        if (names.size() != parameters.size()) {
            Rcpp::stop("routing_parameters must be a named list");
        }
        for (R_xlen_t index = 0; index < parameters.size(); ++index) {
            options.parameters[Rcpp::as<std::string>(names[index])] =
                    Rcpp::as<double>(parameters[index]);
        }
    }
    auto native_edges = as_edges(edges);
    if (source_points.nrow() != edges.nrow() || source_points.ncol() != 2 ||
            target_points.nrow() != edges.nrow() || target_points.ncol() != 2 ||
            source_directions.size() != edges.nrow() ||
            target_directions.size() != edges.nrow()) {
        Rcpp::stop("edge routing option lengths are inconsistent");
    }
    for (int row = 0; row < edges.nrow(); ++row) {
        if (!Rcpp::NumericVector::is_na(source_points(row, 0)) &&
                !Rcpp::NumericVector::is_na(source_points(row, 1))) {
            native_edges[row].has_source_point = true;
            native_edges[row].source_point = {
                    source_points(row, 0), source_points(row, 1)};
        }
        if (!Rcpp::NumericVector::is_na(target_points(row, 0)) &&
                !Rcpp::NumericVector::is_na(target_points(row, 1))) {
            native_edges[row].has_target_point = true;
            native_edges[row].target_point = {
                    target_points(row, 0), target_points(row, 1)};
        }
        native_edges[row].source_directions = source_directions[row];
        native_edges[row].target_directions = target_directions[row];
    }
    const auto routes = adaptagrams::route_edges(
            as_rectangles(rectangles), native_edges, options);
    Rcpp::List result(routes.size());
    for (std::size_t index = 0; index < routes.size(); ++index) {
        result[index] = as_matrix(routes[index]);
    }
    return result;
}

// [[Rcpp::export]]
SEXP native_layout(
        Rcpp::NumericMatrix rectangles,
        Rcpp::IntegerMatrix edges,
        double ideal_edge_length,
        bool avoid_node_overlaps,
        unsigned int max_iterations) {
    adaptagrams::LayoutOptions options;
    options.ideal_edge_length = ideal_edge_length;
    options.avoid_overlaps = avoid_node_overlaps;
    options.max_iterations = max_iterations;
    return as_matrix(adaptagrams::layout_graph(
            as_rectangles(rectangles), as_edges(edges), options));
}

// [[Rcpp::export]]
SEXP native_avoid_overlaps(
        Rcpp::NumericMatrix rectangles,
        unsigned int max_iterations) {
    return as_matrix(adaptagrams::avoid_overlaps(
            as_rectangles(rectangles), max_iterations));
}
