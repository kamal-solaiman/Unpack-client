// SPDX-License-Identifier: MIT
#include "crc32.h"

namespace m2 {
namespace {

uint32_t kTable[256];
bool kTableReady = false;

void buildTable() {
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t c = i;
        for (int k = 0; k < 8; ++k) c = (c & 1) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
        kTable[i] = c;
    }
    kTableReady = true;
}

}  // namespace

uint32_t crc32Init() { return 0xFFFFFFFFu; }

uint32_t crc32Update(uint32_t crc, const void* data, size_t len) {
    if (!kTableReady) buildTable();
    const uint8_t* p = static_cast<const uint8_t*>(data);
    for (size_t i = 0; i < len; ++i) crc = kTable[(crc ^ p[i]) & 0xFF] ^ (crc >> 8);
    return crc;
}

uint32_t crc32(const void* data, size_t len) { return crc32Update(crc32Init(), data, len) ^ 0xFFFFFFFFu; }

uint32_t crc32NoXorOut(const void* data, size_t len) { return crc32Update(crc32Init(), data, len); }

uint32_t crc32ZeroInit(const void* data, size_t len) { return crc32Update(0, data, len); }

bool crc32Matches(uint32_t expected, const void* data, size_t len) {
    if (expected == 0) return true;  // many tools store 0 when the CRC is unknown
    const uint32_t acc = crc32Update(crc32Init(), data, len);
    return expected == (acc ^ 0xFFFFFFFFu) || expected == acc || expected == crc32ZeroInit(data, len);
}

}  // namespace m2
