#ifndef ADAPTAGRAMS_ADAPTER_HPP
#define ADAPTAGRAMS_ADAPTER_HPP

#include <map>
#include <string>
#include <utility>
#include <vector>

namespace adaptagrams {

struct Point {
    double x;
    double y;
};

struct Rectangle {
    double x;
    double y;
    double width;
    double height;
};

struct Edge {
    std::size_t source;
    std::size_t target;
    bool has_source_point = false;
    Point source_point{0.0, 0.0};
    bool has_target_point = false;
    Point target_point{0.0, 0.0};
    unsigned int source_directions = 15;
    unsigned int target_directions = 15;
};

struct RoutingOptions {
    std::string routing = "orthogonal";
    std::map<std::string, double> parameters;
};

struct LayoutOptions {
    double ideal_edge_length = 100.0;
    bool avoid_overlaps = true;
    unsigned int max_iterations = 100;
};

std::vector<std::vector<Point>> route_edges(
        const std::vector<Rectangle>& rectangles,
        const std::vector<Edge>& edges,
        const RoutingOptions& options);

std::vector<Point> layout_graph(
        const std::vector<Rectangle>& rectangles,
        const std::vector<Edge>& edges,
        const LayoutOptions& options);

std::vector<Point> avoid_overlaps(
        const std::vector<Rectangle>& rectangles,
        unsigned int max_iterations = 100);

}  // namespace adaptagrams

#endif
