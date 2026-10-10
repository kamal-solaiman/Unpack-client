# Simple build for Linux / macOS / MinGW. See README.md for MSVC and CMake.
CXX      ?= g++
CXXSTD   ?= -std=c++17
OPT      ?= -O2
WARN     ?= -Wall -Wextra -Wno-unused-parameter
CXXFLAGS ?= $(CXXSTD) $(OPT) $(WARN)
INCLUDES := -Isrc -Itests
LDFLAGS  ?=

BUILD := build
BIN   := unpack-client
TOOL  := make_fake_client

LIB_SRC := $(filter-out src/main.cpp,$(wildcard src/*.cpp)) tests/testsupport.cpp
ALL_SRC := src/main.cpp $(LIB_SRC)
LIB_OBJ := $(patsubst %.cpp,$(BUILD)/%.o,$(LIB_SRC))
ALL_OBJ := $(patsubst %.cpp,$(BUILD)/%.o,$(ALL_SRC))
TOOL_OBJ := $(BUILD)/tools/make_fake_client.o $(LIB_OBJ)

ifeq ($(OS),Windows_NT)
BIN  := unpack-client.exe
TOOL := make_fake_client.exe
# Static link so the .exe runs on a clean Windows install.
LDFLAGS += -static-libgcc -static-libstdc++ -static
endif

.PHONY: all tools test integration clean testdata

all: $(BIN)

tools: $(BIN) $(TOOL)

$(BIN): $(ALL_OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $(ALL_OBJ) $(LDFLAGS)

$(TOOL): $(TOOL_OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $(TOOL_OBJ) $(LDFLAGS)

$(BUILD)/%.o: %.cpp
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Built-in unit tests (XTEA, LZO1X, Snappy, containers, index layouts, PE
# parsing and key recovery against synthetic images).
test: $(BIN)
	./$(BIN) test --verbose

# End to end test: builds a synthetic client, unpacks it, diffs the result.
integration: tools
	BIN=./$(BIN) TOOL=./$(TOOL) sh tests/integration.sh

clean:
	rm -rf $(BUILD) $(BIN) $(TOOL) unpack-client.exe make_fake_client.exe

# Regenerates src/testdata.h with the external LZO/Snappy oracles described in
# tests/README.md. Not needed to build or test the tool.
testdata:
	python3 tests/gen_testdata.py $(LZO_ORACLE) > src/testdata.h
