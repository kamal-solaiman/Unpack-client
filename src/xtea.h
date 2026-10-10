// SPDX-License-Identifier: MIT
// XTEA (the cipher Metin2 calls "TEA") used by every Crypted Object.
#pragma once

#include <cstdint>
#include <optional>
#include <string>

#include "util.h"

namespace m2 {

constexpr uint32_t kXteaDelta = 0x9E3779B9u;
constexpr int kXteaRounds = 32;

struct XteaKey {
    uint32_t w[4] = {0, 0, 0, 0};

    bool operator==(const XteaKey& o) const {
        return w[0] == o.w[0] && w[1] == o.w[1] && w[2] == o.w[2] && w[3] == o.w[3];
    }
    bool isZero() const { return (w[0] | w[1] | w[2] | w[3]) == 0; }

    // The 16 raw bytes as they appear inside the executable / on disk.
    Bytes toBytes() const;
    std::string toByteHex() const;                      // "b9 9e b0 02 6f ..."
    std::string toDwordArray() const;                   // "[ 45129401, 92367215, ... ]"
    std::string toHexArray() const;                     // "[ 0x02B09EB9, ... ]"

    static XteaKey fromBytes(const uint8_t* p);         // 16 bytes, little-endian dwords
    static std::optional<XteaKey> parse(const std::string& s);
};

void xteaDecryptBlock(uint32_t& y, uint32_t& z, const XteaKey& key);
void xteaEncryptBlock(uint32_t& y, uint32_t& z, const XteaKey& key);

// In-place, whole 8-byte blocks only (trailing bytes are left untouched).
void xteaDecryptBlocks(uint8_t* data, size_t len, const XteaKey& key);
void xteaEncryptBlocks(uint8_t* data, size_t len, const XteaKey& key);

// Metin2 semantics: the buffer is zero padded up to a multiple of 8 bytes.
// The result is exactly `roundUp8(len)` bytes long.
Bytes xteaDecryptPadded(const uint8_t* data, size_t len, const XteaKey& key);
Bytes xteaEncryptPadded(const uint8_t* data, size_t len, const XteaKey& key);

inline size_t roundUp8(size_t n) { return (n + 7) & ~static_cast<size_t>(7); }

}  // namespace m2
