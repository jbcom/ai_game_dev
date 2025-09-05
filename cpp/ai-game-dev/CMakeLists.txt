cmake_minimum_required(VERSION 3.16)
project(ai-game-dev-cpp)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(PkgConfig REQUIRED)

# Set up library paths
set(GO_LIB_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../go/lib)
set(CORE_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../core/ai-game-dev/include)

# Include directories
include_directories(
    ${CORE_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Link directories
link_directories(${GO_LIB_DIR})

# Create the main C++ wrapper library
add_library(ai-game-dev-cpp SHARED
    src/ai_game_dev.cpp
    src/game_generator.cpp
    src/bevy_integration.cpp
    src/godot_integration.cpp
    src/utils.cpp
)

# Link against the Go shared library
target_link_libraries(ai-game-dev-cpp
    ai_game_dev  # Go shared library
    dl
    pthread
)

# Set library properties
set_target_properties(ai-game-dev-cpp PROPERTIES
    VERSION 1.0.0
    SOVERSION 1
    PUBLIC_HEADER "include/ai_game_dev.hpp;include/game_generator.hpp"
)

# Create example executables
add_executable(ai-game-dev-example examples/basic_usage.cpp)
target_link_libraries(ai-game-dev-example ai-game-dev-cpp)

add_executable(bevy-integration-example examples/bevy_integration.cpp)  
target_link_libraries(bevy-integration-example ai-game-dev-cpp)

# Install targets
install(TARGETS ai-game-dev-cpp
    LIBRARY DESTINATION lib
    PUBLIC_HEADER DESTINATION include/ai-game-dev
)

install(TARGETS ai-game-dev-example bevy-integration-example
    RUNTIME DESTINATION bin
)

# Create pkg-config file
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/ai-game-dev.pc.in
    ${CMAKE_CURRENT_BINARY_DIR}/ai-game-dev.pc
    @ONLY
)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/ai-game-dev.pc
    DESTINATION lib/pkgconfig
)

# Testing
enable_testing()
add_subdirectory(tests)