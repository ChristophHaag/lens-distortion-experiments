cmake_minimum_required(VERSION 2.6)
project(distortion)

INCLUDE_DIRECTORIES(${CMAKE_CURRENT_SOURCE_DIR}/stb)

link_libraries(m)

add_executable(distortion main.c)

install(TARGETS distortion RUNTIME DESTINATION bin)
