cmake_minimum_required(VERSION 3.16)
project(Alt2Unpacker LANGUAGES CXX)

add_executable(Alt2Unpacker main.cpp)
target_compile_features(Alt2Unpacker PRIVATE cxx_std_17)

if(MSVC)
    target_compile_options(Alt2Unpacker PRIVATE /W4 /permissive- /utf-8)
else()
    target_compile_options(Alt2Unpacker PRIVATE -Wall -Wextra -Wpedantic)
endif()
