# Verification report

Date: 2026-09-18. Host: Linux x86-64 under WSL2. Adaptagrams commit:
`840ebcff20dbba36ad03a2160edf7cbaf9859984`.

## Successful checks

- Upstream libavoid `example.cpp`: compiled with GCC 13.3.0 and ran.
- Shared C++ adapter: CMake build and CTest, 1/1 passed.
- AddressSanitizer C++ adapter build: 1/1 passed with leak detection enabled.
- Python editable/source install on Python 3.12.3 and python-igraph 0.11.9:
  26/26 pytest tests passed.
- Python installed wheel on Python 3.14.6 and python-igraph 1.0.0:
  26/26 pytest tests passed from outside the source tree.
- Ruff formatting/lint: passed.
- Python sdist and Linux CPython 3.14 wheel: built successfully.
- R source package on R 4.5.1 and R igraph 1.6.0: installed; 81 testthat
  expectations passed.
- `R CMD check --no-manual`: status OK, including vignette rebuild.
- Cross-language fixed obstacle fixture: all four points matched with relative
  and absolute tolerance `1e-9`.
- Required Python/R examples and SVG exporter: executed successfully.

macOS and Windows were not available locally. They are configured in GitHub
Actions and are not claimed as verified until those jobs pass.

## Resolved failures during development

- The first native build rejected a const call to libavoid's mutable
  `displayRoute()` API; connector access was corrected.
- libcola's optional `output_svg.cpp` expected an Autotools-generated
  `config.h`; that unused translation unit is excluded from the CMake target.
- The first R route call attempted to read names from an empty parameter list;
  empty lists are now handled before name conversion.
- Two R fixed-port assertions differed only in matrix column names; the tests
  now compare coordinate values without names.
- The initial Python sdist referenced the monorepo parent. Both packages now
  contain synchronized native source snapshots and build independently.
- An initial 1,000-node benchmark exceeded 30 seconds and was stopped. No
  incomplete result is reported; reproducible drivers retain configurable
  graph sizes.

There are no remaining failing local tests or `R CMD check` warnings.
