cmake_minimum_required(VERSION 3.16)
project(unpack_client CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)
endif()

file(GLOB UNPACK_LIB_SRC CONFIGURE_DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp)
list(REMOVE_ITEM UNPACK_LIB_SRC ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp)

add_library(unpack_client_core STATIC ${UNPACK_LIB_SRC} ${CMAKE_CURRENT_SOURCE_DIR}/tests/testsupport.cpp)
target_include_directories(unpack_client_core PUBLIC src tests)

if(MSVC)
    target_compile_options(unpack_client_core PRIVATE /W3 /utf-8 /EHsc)
    target_compile_definitions(unpack_client_core PUBLIC _CRT_SECURE_NO_WARNINGS NOMINMAX)
    # Static runtime so the .exe does not need the VC++ redistributable.
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
else()
    target_compile_options(unpack_client_core PRIVATE -Wall -Wextra -Wno-unused-parameter)
endif()

add_executable(unpack-client src/main.cpp)
target_link_libraries(unpack-client PRIVATE unpack_client_core)
set_target_properties(unpack-client PROPERTIES OUTPUT_NAME "unpack-client")

add_executable(make_fake_client tools/make_fake_client.cpp)
target_link_libraries(make_fake_client PRIVATE unpack_client_core)

if(MINGW)
    foreach(tgt unpack-client make_fake_client)
        target_link_options(${tgt} PRIVATE -static -static-libgcc -static-libstdc++)
    endforeach()
endif()

enable_testing()
add_test(NAME selftest COMMAND unpack-client test)
add_test(NAME integration
         COMMAND ${CMAKE_COMMAND} -E env
                 BIN=$<TARGET_FILE:unpack-client>
                 TOOL=$<TARGET_FILE:make_fake_client>
                 sh ${CMAKE_CURRENT_SOURCE_DIR}/tests/integration.sh)

install(TARGETS unpack-client RUNTIME DESTINATION bin)
