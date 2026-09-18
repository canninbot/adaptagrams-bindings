# Benchmark notes

Measured on 2026-09-18 under WSL2 Linux x86-64, AMD Ryzen 7 PRO 6850H
(16 logical CPUs), 23 GiB RAM, GCC 13.3.0, and CMake 3.28.3. Python used
3.14.6, python-igraph 1.0.0, and NumPy 2.5.3. R ran in an Ubuntu 24.04 Docker
container using R 4.5.1 and igraph 1.6.0.

| Language | Vertices/edges | Conversion | Layout | Routing | End-to-end |
|---|---:|---:|---:|---:|---:|
| Python | 10 | 0.00043 s | 0.00063 s | 0.00187 s | 0.00284 s |
| Python | 100 | 0.00282 s | 0.53326 s | 0.15044 s | 0.70319 s |
| R | 10 | included in calls | 0.001 s | 0.003 s | 0.002 s |
| R | 100 | included in calls | 0.566 s | 0.148 s | 0.736 s |

Python peak memory attributed by `tracemalloc` was 10,219 bytes at 10 vertices
and 103,668 bytes at 100 vertices; this excludes most C++ allocations and is
therefore not a process-memory measurement. The R driver reports operation
timings but does not claim a native-memory figure.

The initial 1,000-node end-to-end run exceeded 30 seconds in this environment,
so it was stopped and no incomplete number is reported. The scripts retain the
requested 10, 100, 1,000, and 10,000 defaults; use explicit smaller sizes when
testing constrained hardware. libcola's dense internal distance matrices make
large graph layouts expensive.
