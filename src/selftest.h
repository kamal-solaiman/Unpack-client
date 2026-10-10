// SPDX-License-Identifier: MIT
// Built in self tests (`unpack-client test`). They exercise every layer with
// reference data: XTEA, CRC32, the LZO1X decoder (against streams produced by
// the real LZO compressor), Snappy, the Crypted Object container, the EterPack
// index reader and the key recovery against a synthetic PE image.
#pragma once

namespace m2 {

// Returns 0 when everything passed, 1 otherwise.
int runSelfTests(bool verbose);

}  // namespace m2
