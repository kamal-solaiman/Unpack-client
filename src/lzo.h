// SPDX-License-Identifier: MIT
// LZO1X decompressor (independent implementation of the public LZO1X format,
// which is what the Metin2 client uses for MCOZ Crypted Objects).
#pragma once

#include <cstddef>
#include <cstdint>
#include <string>

#include "util.h"

namespace m2 {

// Upper bound of the decompressed size is supplied by the caller (the
// Crypted Object header stores it). Returns false on malformed input or when
// the output buffer is too small.
bool lzo1xDecompress(const uint8_t* in, size_t inLen, uint8_t* out, size_t outCap,
                     size_t& outLen, std::string* err = nullptr);

// Convenience wrapper returning a buffer. `expectedSize` is the real (plain)
// size; when it is unknown pass 0 and a growing buffer will be used.
bool lzo1xDecompressTo(const uint8_t* in, size_t inLen, size_t expectedSize, Bytes& out,
                       std::string* err = nullptr);

// "Stored" LZO1X stream: a single literal run plus the end-of-stream marker.
// Valid LZO1X (every LZO1X decoder accepts it) but it does not shrink the
// data. Used by the test suite to build synthetic MCOZ containers without
// pulling a compressor dependency in.
size_t lzo1xStoredBound(size_t inLen);
bool lzo1xStore(const uint8_t* in, size_t inLen, Bytes& out);

}  // namespace m2
