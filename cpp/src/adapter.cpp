#include "adaptagrams/adapter.hpp"

#include <cmath>
#include <memory>
#include <stdexcept>
#include <unordered_map>

#include "libavoid/libavoid.h"
#include "libcola/cola.h"
#include "libvpsc/rectangle.h"

namespace adaptagrams {
namespace {

void validate_rectangles(const std::vector<Rectangle>& rectangles) {
    for (std::size_t index = 0; index < rectangles.size(); ++index) {
        const auto& rectangle = rectangles[index];
        if (!std::isfinite(rectangle.x) || !std::isfinite(rectangle.y) ||
                !std::isfinite(rectangle.width) ||
                !std::isfinite(rectangle.height)) {
            throw std::invalid_argument(
                    "vertex " + std::to_string(index) +
                    " geometry must be finite");
        }
        if (rectangle.width <= 0.0 || rectangle.height <= 0.0) {
            throw std::invalid_argument(
                    "vertex " + std::to_string(index) +
                    " width and height must be positive");
        }
    }
}

void validate_edges(
        const std::vector<Edge>& edges,
        std::size_t vertex_count,
        bool allow_self_loops) {
    for (std::size_t index = 0; index < edges.size(); ++index) {
        const auto& edge = edges[index];
        if (edge.source >= vertex_count || edge.target >= vertex_count) {
            throw std::invalid_argument(
                    "edge " + std::to_string(index) +
                    " references an invalid vertex index");
        }
        if (!allow_self_loops && edge.source == edge.target) {
            throw std::invalid_argument(
                    "edge " + std::to_string(index) +
                    " is a self-loop; libavoid self-loop routing is not "
                    "supported by this adapter");
        }
    }
}

Avoid::Point center(const Rectangle& rectangle) {
    return Avoid::Point(rectangle.x, rectangle.y);
}

Avoid::Polygon polygon(const Rectangle& rectangle) {
    const double half_width = rectangle.width / 2.0;
    const double half_height = rectangle.height / 2.0;
    Avoid::Rectangle avoid_rectangle(
            Avoid::Point(
                    rectangle.x - half_width,
                    rectangle.y - half_height),
            Avoid::Point(
                    rectangle.x + half_width,
                    rectangle.y + half_height));
    return avoid_rectangle;
}

Avoid::RoutingParameter routing_parameter(const std::string& name) {
    static const std::unordered_map<std::string, Avoid::RoutingParameter>
            parameter_map = {
                {"segment_penalty", Avoid::segmentPenalty},
                {"angle_penalty", Avoid::anglePenalty},
                {"crossing_penalty", Avoid::crossingPenalty},
                {"cluster_crossing_penalty", Avoid::clusterCrossingPenalty},
                {"fixed_shared_path_penalty", Avoid::fixedSharedPathPenalty},
                {"port_direction_penalty", Avoid::portDirectionPenalty},
                {"shape_buffer_distance", Avoid::shapeBufferDistance},
                {"ideal_nudging_distance", Avoid::idealNudgingDistance},
                {"reverse_direction_penalty", Avoid::reverseDirectionPenalty},
            };
    const auto parameter = parameter_map.find(name);
    if (parameter == parameter_map.end()) {
        throw std::invalid_argument("unknown routing parameter: " + name);
    }
    return parameter->second;
}

std::vector<vpsc::Rectangle*> make_layout_rectangles(
        const std::vector<Rectangle>& rectangles) {
    std::vector<vpsc::Rectangle*> result;
    result.reserve(rectangles.size());
    for (const auto& rectangle : rectangles) {
        const double half_width = rectangle.width / 2.0;
        const double half_height = rectangle.height / 2.0;
        result.push_back(new vpsc::Rectangle(
                rectangle.x - half_width,
                rectangle.x + half_width,
                rectangle.y - half_height,
                rectangle.y + half_height));
    }
    return result;
}

class LayoutRectangles {
public:
    explicit LayoutRectangles(const std::vector<Rectangle>& rectangles)
        : rectangles_(make_layout_rectangles(rectangles)) {}

    ~LayoutRectangles() {
        for (auto* rectangle : rectangles_) {
            delete rectangle;
        }
    }

    LayoutRectangles(const LayoutRectangles&) = delete;
    LayoutRectangles& operator=(const LayoutRectangles&) = delete;

    vpsc::Rectangles& get() { return rectangles_; }

private:
    vpsc::Rectangles rectangles_;
};

std::vector<Point> rectangle_centers(const vpsc::Rectangles& rectangles) {
    std::vector<Point> result;
    result.reserve(rectangles.size());
    for (const auto* rectangle : rectangles) {
        result.push_back(
                {rectangle->getCentreX(), rectangle->getCentreY()});
    }
    return result;
}

}  // namespace

std::vector<std::vector<Point>> route_edges(
        const std::vector<Rectangle>& rectangles,
        const std::vector<Edge>& edges,
        const RoutingOptions& options) {
    validate_rectangles(rectangles);
    validate_edges(edges, rectangles.size(), false);

    unsigned int router_flags = 0;
    Avoid::ConnType connection_type = Avoid::ConnType_None;
    if (options.routing == "orthogonal") {
        router_flags = Avoid::OrthogonalRouting;
        connection_type = Avoid::ConnType_Orthogonal;
    } else if (options.routing == "polyline") {
        router_flags = Avoid::PolyLineRouting;
        connection_type = Avoid::ConnType_PolyLine;
    } else {
        throw std::invalid_argument(
                "routing must be 'orthogonal' or 'polyline'");
    }

    auto router = std::make_unique<Avoid::Router>(router_flags);
    for (const auto& [name, value] : options.parameters) {
        if (!std::isfinite(value) || value < 0.0) {
            throw std::invalid_argument(
                    "routing parameter " + name +
                    " must be finite and nonnegative");
        }
        router->setRoutingParameter(routing_parameter(name), value);
    }

    // Router owns all shapes and connectors registered with it.
    for (std::size_t index = 0; index < rectangles.size(); ++index) {
        Avoid::Polygon shape_polygon = polygon(rectangles[index]);
        new Avoid::ShapeRef(
                router.get(), shape_polygon, static_cast<unsigned int>(index + 1));
    }

    std::vector<Avoid::ConnRef*> connectors;
    connectors.reserve(edges.size());
    for (std::size_t index = 0; index < edges.size(); ++index) {
        const auto& edge = edges[index];
        const Avoid::Point source = edge.has_source_point
                ? Avoid::Point(edge.source_point.x, edge.source_point.y)
                : center(rectangles[edge.source]);
        const Avoid::Point target = edge.has_target_point
                ? Avoid::Point(edge.target_point.x, edge.target_point.y)
                : center(rectangles[edge.target]);
        const Avoid::ConnEnd source_end(source, edge.source_directions);
        const Avoid::ConnEnd target_end(target, edge.target_directions);
        auto* connector = new Avoid::ConnRef(
                router.get(), source_end, target_end,
                static_cast<unsigned int>(rectangles.size() + index + 1));
        connector->setRoutingType(connection_type);
        connectors.push_back(connector);
    }
    router->processTransaction();

    std::vector<std::vector<Point>> routes;
    routes.reserve(connectors.size());
    for (auto* connector : connectors) {
        std::vector<Point> route;
        const auto& display_route = connector->displayRoute();
        route.reserve(display_route.ps.size());
        for (const auto& point : display_route.ps) {
            route.push_back({point.x, point.y});
        }
        routes.push_back(std::move(route));
    }
    return routes;
}

std::vector<Point> layout_graph(
        const std::vector<Rectangle>& rectangles,
        const std::vector<Edge>& edges,
        const LayoutOptions& options) {
    validate_rectangles(rectangles);
    validate_edges(edges, rectangles.size(), true);
    if (rectangles.empty()) {
        return {};
    }
    if (!std::isfinite(options.ideal_edge_length) ||
            options.ideal_edge_length <= 0.0) {
        throw std::invalid_argument(
                "ideal_edge_length must be finite and positive");
    }

    LayoutRectangles layout_rectangles(rectangles);
    std::vector<cola::Edge> layout_edges;
    layout_edges.reserve(edges.size());
    for (const auto& edge : edges) {
        if (edge.source != edge.target) {
            layout_edges.emplace_back(edge.source, edge.target);
        }
    }
    cola::TestConvergence convergence(1e-4, options.max_iterations);
    cola::ConstrainedFDLayout layout(
            layout_rectangles.get(), layout_edges,
            options.ideal_edge_length, cola::StandardEdgeLengths,
            &convergence);
    layout.setAvoidNodeOverlaps(options.avoid_overlaps);
    layout.run();
    return rectangle_centers(layout_rectangles.get());
}

std::vector<Point> avoid_overlaps(
        const std::vector<Rectangle>& rectangles,
        unsigned int max_iterations) {
    validate_rectangles(rectangles);
    if (rectangles.empty()) {
        return {};
    }
    LayoutRectangles layout_rectangles(rectangles);
    const std::vector<cola::Edge> no_edges;
    cola::TestConvergence convergence(1e-4, max_iterations);
    cola::ConstrainedFDLayout layout(
            layout_rectangles.get(), no_edges, 1.0,
            cola::StandardEdgeLengths, &convergence);
    layout.setAvoidNodeOverlaps(true);
    layout.run();
    return rectangle_centers(layout_rectangles.get());
}

}  // namespace adaptagrams
