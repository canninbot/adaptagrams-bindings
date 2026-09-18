// Generated registration wrappers for the stable native API.
#include <Rcpp.h>
#include <R_ext/Rdynload.h>

SEXP native_route(
        Rcpp::NumericMatrix,
        Rcpp::IntegerMatrix,
        std::string,
        Rcpp::List,
        Rcpp::NumericMatrix,
        Rcpp::NumericMatrix,
        Rcpp::IntegerVector,
        Rcpp::IntegerVector);
SEXP native_layout(
        Rcpp::NumericMatrix,
        Rcpp::IntegerMatrix,
        double,
        bool,
        unsigned int);
SEXP native_avoid_overlaps(Rcpp::NumericMatrix, unsigned int);

extern "C" SEXP _adaptagrams_native_route(
        SEXP rectangles,
        SEXP edges,
        SEXP routing,
        SEXP parameters,
        SEXP source_points,
        SEXP target_points,
        SEXP source_directions,
        SEXP target_directions) {
    BEGIN_RCPP
    return native_route(
            Rcpp::as<Rcpp::NumericMatrix>(rectangles),
            Rcpp::as<Rcpp::IntegerMatrix>(edges),
            Rcpp::as<std::string>(routing),
            Rcpp::as<Rcpp::List>(parameters),
            Rcpp::as<Rcpp::NumericMatrix>(source_points),
            Rcpp::as<Rcpp::NumericMatrix>(target_points),
            Rcpp::as<Rcpp::IntegerVector>(source_directions),
            Rcpp::as<Rcpp::IntegerVector>(target_directions));
    END_RCPP
}

extern "C" SEXP _adaptagrams_native_layout(
        SEXP rectangles,
        SEXP edges,
        SEXP ideal_edge_length,
        SEXP avoid_node_overlaps,
        SEXP max_iterations) {
    BEGIN_RCPP
    return native_layout(
            Rcpp::as<Rcpp::NumericMatrix>(rectangles),
            Rcpp::as<Rcpp::IntegerMatrix>(edges),
            Rcpp::as<double>(ideal_edge_length),
            Rcpp::as<bool>(avoid_node_overlaps),
            Rcpp::as<unsigned int>(max_iterations));
    END_RCPP
}

extern "C" SEXP _adaptagrams_native_avoid_overlaps(
        SEXP rectangles,
        SEXP max_iterations) {
    BEGIN_RCPP
    return native_avoid_overlaps(
            Rcpp::as<Rcpp::NumericMatrix>(rectangles),
            Rcpp::as<unsigned int>(max_iterations));
    END_RCPP
}

static const R_CallMethodDef call_entries[] = {
    {"_adaptagrams_native_route", (DL_FUNC) &_adaptagrams_native_route, 8},
    {"_adaptagrams_native_layout", (DL_FUNC) &_adaptagrams_native_layout, 5},
    {
        "_adaptagrams_native_avoid_overlaps",
        (DL_FUNC) &_adaptagrams_native_avoid_overlaps,
        2
    },
    {NULL, NULL, 0}
};

extern "C" void R_init_adaptagrams(DllInfo* dll) {
    R_registerRoutines(dll, NULL, call_entries, NULL, NULL);
    R_useDynamicSymbols(dll, FALSE);
}
