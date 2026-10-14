cmake_minimum_required(VERSION 3.10)
project(UnpackTool)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(src)
include_directories(src/lzo)

# Source files
set(SOURCES
    src/main.cpp
    src/xtea.cpp
    src/eterpack.cpp
    src/key_extractor.cpp
    src/filetype.cpp
    src/crypted_object.cpp
    src/lzo/minilzo.c
)

# Executable
add_executable(UnpackTool ${SOURCES})

# For MSVC
if(MSVC)
    target_compile_options(UnpackTool PRIVATE /W3 /EHsc)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
else()
    target_compile_options(UnpackTool PRIVATE -Wall -Wextra -O2)
endif()

# Link filesystem for older compilers
if(UNIX AND NOT APPLE)
    target_link_libraries(UnpackTool stdc++fs)
endif()

# Output directory
set_target_properties(UnpackTool PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

message(STATUS "UnpackTool configured")
message(STATUS "Build with: cmake --build . --config Release")
