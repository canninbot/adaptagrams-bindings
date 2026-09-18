#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "adaptagrams/adapter.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_native, module) {
    module.doc() = "Native Adaptagrams routing and layout adapter";

    py::class_<adaptagrams::Point>(module, "Point")
            .def(py::init<double, double>())
            .def_readwrite("x", &adaptagrams::Point::x)
            .def_readwrite("y", &adaptagrams::Point::y);

    py::class_<adaptagrams::Rectangle>(module, "Rectangle")
            .def(py::init<double, double, double, double>())
            .def_readwrite("x", &adaptagrams::Rectangle::x)
            .def_readwrite("y", &adaptagrams::Rectangle::y)
            .def_readwrite("width", &adaptagrams::Rectangle::width)
            .def_readwrite("height", &adaptagrams::Rectangle::height);

    py::class_<adaptagrams::Edge>(module, "Edge")
            .def(py::init<std::size_t, std::size_t>())
            .def_readwrite("source", &adaptagrams::Edge::source)
            .def_readwrite("target", &adaptagrams::Edge::target)
            .def_readwrite("has_source_point", &adaptagrams::Edge::has_source_point)
            .def_readwrite("source_point", &adaptagrams::Edge::source_point)
            .def_readwrite("has_target_point", &adaptagrams::Edge::has_target_point)
            .def_readwrite("target_point", &adaptagrams::Edge::target_point)
            .def_readwrite(
                    "source_directions", &adaptagrams::Edge::source_directions)
            .def_readwrite(
                    "target_directions", &adaptagrams::Edge::target_directions);

    py::class_<adaptagrams::RoutingOptions>(module, "RoutingOptions")
            .def(py::init<>())
            .def_readwrite("routing", &adaptagrams::RoutingOptions::routing)
            .def_readwrite("parameters", &adaptagrams::RoutingOptions::parameters);

    py::class_<adaptagrams::LayoutOptions>(module, "LayoutOptions")
            .def(py::init<>())
            .def_readwrite(
                    "ideal_edge_length",
                    &adaptagrams::LayoutOptions::ideal_edge_length)
            .def_readwrite(
                    "avoid_overlaps", &adaptagrams::LayoutOptions::avoid_overlaps)
            .def_readwrite(
                    "max_iterations", &adaptagrams::LayoutOptions::max_iterations);

    module.def("route_edges", &adaptagrams::route_edges);
    module.def("layout_graph", &adaptagrams::layout_graph);
    module.def("avoid_overlaps", &adaptagrams::avoid_overlaps);
}
