// SPDX-License-Identifier: MIT
// Raw Snappy decompression (used by MCSP Crypted Objects, pack type 6).
#pragma once

#include <cstddef>
#include <cstdint>
#include <string>

#include "util.h"

namespace m2 {

// Reads the varint preamble of a raw snappy stream.
bool snappyUncompressedLength(const uint8_t* in, size_t inLen, size_t& length, std::string* err = nullptr);

bool snappyDecompress(const uint8_t* in, size_t inLen, uint8_t* out, size_t outCap,
                      size_t& outLen, std::string* err = nullptr);
bool snappyDecompressTo(const uint8_t* in, size_t inLen, size_t expectedSize, Bytes& out,
                        std::string* err = nullptr);

// True when the buffer starts with the snappy *framing* magic; such streams are
// handled by snappyDecompressTo as well (frames are concatenated).
bool snappyLooksFramed(const uint8_t* in, size_t inLen);

// Literal-only ("stored") snappy stream, for the test suite.
bool snappyStore(const uint8_t* in, size_t inLen, Bytes& out);

}  // namespace m2
