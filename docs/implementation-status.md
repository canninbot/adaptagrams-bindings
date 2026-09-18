# Implementation status

Upstream Adaptagrams commit: `840ebcff20dbba36ad03a2160edf7cbaf9859984`.

Implemented and tested: libavoid orthogonal/polyline routing, rectangular
obstacles, fixed endpoints, endpoint directions, routing parameters, libcola
layout, libvpsc-backed overlap prevention, native Python/R igraph round trips,
ordinary structures, biological metadata, multiedges, empty graphs, and output
reuse.

Not implemented: libtopology, libdialect, arbitrary public VPSC constraint
construction, shape connection-pin class selection, checkpoint routing, and
self-loop routing. The packages do not claim SBGN rendering or compliance;
they preserve SBGN metadata and supply geometry for a future renderer.

Local verification is Linux x86-64 only. CI definitions target Linux, macOS,
and Windows. Passing configuration on those runners is required before a
platform is described as verified in a release.
