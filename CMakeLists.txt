cmake_minimum_required(VERSION 3.18)
project(adaptagrams_bindings LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(ADAPTAGRAMS_SOURCE_DIR
    "${CMAKE_CURRENT_SOURCE_DIR}/third_party/adaptagrams/cola")

file(GLOB LIBAVOID_SOURCES CONFIGURE_DEPENDS
    "${ADAPTAGRAMS_SOURCE_DIR}/libavoid/*.cpp")
file(GLOB LIBVPSC_SOURCES CONFIGURE_DEPENDS
    "${ADAPTAGRAMS_SOURCE_DIR}/libvpsc/*.cpp")
file(GLOB LIBCOLA_SOURCES CONFIGURE_DEPENDS
    "${ADAPTAGRAMS_SOURCE_DIR}/libcola/*.cpp")
list(REMOVE_ITEM LIBCOLA_SOURCES
    "${ADAPTAGRAMS_SOURCE_DIR}/libcola/output_svg.cpp")

add_library(adaptagrams_native STATIC
    cpp/src/adapter.cpp
    ${LIBAVOID_SOURCES}
    ${LIBVPSC_SOURCES}
    ${LIBCOLA_SOURCES})
target_include_directories(adaptagrams_native PUBLIC
    cpp/include
    "${ADAPTAGRAMS_SOURCE_DIR}")
target_compile_definitions(adaptagrams_native PRIVATE NDEBUG)

option(ADAPTAGRAMS_BUILD_PYTHON "Build the Python extension" ON)
if(ADAPTAGRAMS_BUILD_PYTHON)
    find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
    find_package(pybind11 CONFIG REQUIRED)
    pybind11_add_module(_native MODULE cpp/src/python_bindings.cpp)
    target_link_libraries(_native PRIVATE adaptagrams_native)
    install(TARGETS _native DESTINATION pyadaptagrams)
endif()

option(ADAPTAGRAMS_BUILD_CPP_TESTS "Build C++ tests" OFF)
if(ADAPTAGRAMS_BUILD_CPP_TESTS)
    enable_testing()
    add_executable(adapter_smoke_test cpp/tests/adapter_smoke_test.cpp)
    target_link_libraries(adapter_smoke_test PRIVATE adaptagrams_native)
    add_test(NAME adapter_smoke_test COMMAND adapter_smoke_test)
endif()
