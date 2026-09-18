#include "adaptagrams/adapter.hpp"

#include <cassert>

int main() {
    const std::vector<adaptagrams::Rectangle> rectangles = {
        {0.0, 0.0, 80.0, 40.0},
        {200.0, 0.0, 80.0, 40.0},
        {100.0, 0.0, 40.0, 40.0},
    };
    const std::vector<adaptagrams::Edge> edges = {{0, 1}};
    const auto routes = adaptagrams::route_edges(
            rectangles, edges, adaptagrams::RoutingOptions{});
    assert(routes.size() == 1);
    assert(routes.front().size() >= 2);
    return 0;
}
