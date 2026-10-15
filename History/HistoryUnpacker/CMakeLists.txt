cmake_minimum_required(VERSION 3.20)
project(HistoryUnpacker VERSION 1.0 LANGUAGES C CXX)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
add_library(history_core src/history.cpp third_party/aes/aes.c)
target_include_directories(history_core PUBLIC src PRIVATE third_party/aes third_party/xxhash)
target_compile_definitions(history_core PRIVATE AES256=1 CBC=0 CTR=0 ECB=1)
if(MSVC)
  target_compile_options(history_core PRIVATE /W4 /utf-8)
else()
  target_compile_options(history_core PRIVATE -Wall -Wextra -Wpedantic)
endif()
add_executable(HistoryUnpacker src/main.cpp)
target_link_libraries(HistoryUnpacker PRIVATE history_core)
add_custom_command(TARGET HistoryUnpacker POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E make_directory "$<TARGET_FILE_DIR:HistoryUnpacker>/data"
  COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/data/history-names.txt" "$<TARGET_FILE_DIR:HistoryUnpacker>/data/history-names.txt")
include(CTest)
if(BUILD_TESTING)
  add_executable(HistoryTests tests/tests.cpp)
  target_link_libraries(HistoryTests PRIVATE history_core)
  add_test(NAME core COMMAND HistoryTests)
  # Generates small valid History D2 archives so integration tests can run
  # without the proprietary fixture. Must use the same AES configuration.
  add_executable(HistoryTestArchive tests/testarchive.cpp)
  target_link_libraries(HistoryTestArchive PRIVATE history_core)
  target_include_directories(HistoryTestArchive PRIVATE third_party/aes third_party/xxhash)
  target_compile_definitions(HistoryTestArchive PRIVATE AES256=1 CBC=0 CTR=0 ECB=1)
  find_package(Python3 COMPONENTS Interpreter QUIET)
  if(Python3_FOUND)
    # Self-contained discovery test with Metin2-style pack names (no fixture needed).
    add_test(NAME history_generated_discovery COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/integration_generated.py"
      "$<TARGET_FILE:HistoryUnpacker>" "$<TARGET_FILE:HistoryTestArchive>")
  endif()
  if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/../pack/workplace.d2")
    add_test(NAME history_sample_verify COMMAND HistoryUnpacker --archive "${CMAKE_CURRENT_SOURCE_DIR}/../pack/workplace.d2" verify)
    # The pack directory itself is a valid --archive argument: every D2 archive in it
    # must be discovered and verified, not only workplace.d2.
    add_test(NAME history_pack_directory_scan COMMAND HistoryUnpacker --archive "${CMAKE_CURRENT_SOURCE_DIR}/../pack" scan)
    add_test(NAME history_pack_directory_verify COMMAND HistoryUnpacker --archive "${CMAKE_CURRENT_SOURCE_DIR}/../pack" verify)
  endif()
endif()
if(BUILD_TESTING AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/../pack/workplace.d2")
  find_package(Python3 COMPONENTS Interpreter QUIET)
  if(Python3_FOUND)
    add_test(NAME history_integration COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/integration.py" "$<TARGET_FILE:HistoryUnpacker>"
      "${CMAKE_CURRENT_SOURCE_DIR}/../pack/workplace.d2")
  endif()
endif()

