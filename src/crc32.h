// SPDX-License-Identifier: MIT
// CRC32 helpers. The client stores a CRC next to every packed file; different
// client revisions finalise the accumulator differently, so verification tries
// all known variants instead of trusting a single one.
#pragma once

#include <cstddef>
#include <cstdint>

namespace m2 {

uint32_t crc32Init();
uint32_t crc32Update(uint32_t crc, const void* data, size_t len);

// zlib/IEEE style: init 0xFFFFFFFF, final xor 0xFFFFFFFF.
uint32_t crc32(const void* data, size_t len);
// init 0xFFFFFFFF, no final xor.
uint32_t crc32NoXorOut(const void* data, size_t len);
// init 0, no final xor.
uint32_t crc32ZeroInit(const void* data, size_t len);

// True when `expected` matches any of the CRC32 variants above.
bool crc32Matches(uint32_t expected, const void* data, size_t len);

}  // namespace m2
