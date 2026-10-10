// SPDX-License-Identifier: MIT
#include "xtea.h"

#include <cstdio>

namespace m2 {

Bytes XteaKey::toBytes() const {
    Bytes out(16);
    for (int i = 0; i < 4; ++i) wr32(out.data() + i * 4, w[i]);
    return out;
}

std::string XteaKey::toByteHex() const {
    Bytes b = toBytes();
    return toHex(b.data(), b.size(), " ");
}

std::string XteaKey::toDwordArray() const {
    char buf[128];
    std::snprintf(buf, sizeof buf, "[%u, %u, %u, %u]", w[0], w[1], w[2], w[3]);
    return buf;
}

std::string XteaKey::toHexArray() const {
    char buf[128];
    std::snprintf(buf, sizeof buf, "[0x%08X, 0x%08X, 0x%08X, 0x%08X]", w[0], w[1], w[2], w[3]);
    return buf;
}

XteaKey XteaKey::fromBytes(const uint8_t* p) {
    XteaKey k;
    for (int i = 0; i < 4; ++i) k.w[i] = rd32(p + i * 4);
    return k;
}

std::optional<XteaKey> XteaKey::parse(const std::string& s) {
    std::string t = trim(s);
    if (t.empty()) return std::nullopt;

    // Form 1: "45129401,92367215,681285731,1710201" or "[0x02b09eb9, ...]"
    std::string cleaned;
    for (char c : t)
        if (!(c == '[' || c == ']' || c == ' ' || c == '\t')) cleaned += c;
    auto parts = split(cleaned, ',');
    if (parts.size() == 4) {
        XteaKey k;
        for (int i = 0; i < 4; ++i) {
            std::string p = trim(parts[i]);
            try {
                k.w[i] = static_cast<uint32_t>(std::stoul(p, nullptr, 0));
            } catch (...) {
                return std::nullopt;
            }
        }
        return k;
    }

    // Form 2: 16 raw bytes in hex, with or without separators.
    Bytes b;
    auto hex = fromHex(t);
    if (hex) b = *hex;
    if (b.size() == 16) return XteaKey::fromBytes(b.data());
    if (b.size() == 8) {  // two dwords only -> pad with zeros
        Bytes padded(16, 0);
        for (size_t i = 0; i < 8; ++i) padded[i] = b[i];
        return XteaKey::fromBytes(padded.data());
    }
    return std::nullopt;
}

void xteaDecryptBlock(uint32_t& y, uint32_t& z, const XteaKey& key) {
    uint32_t sum = kXteaDelta * static_cast<uint32_t>(kXteaRounds);
    for (int i = 0; i < kXteaRounds; ++i) {
        z -= (((y << 4) ^ (y >> 5)) + y) ^ (sum + key.w[(sum >> 11) & 3]);
        sum -= kXteaDelta;
        y -= (((z << 4) ^ (z >> 5)) + z) ^ (sum + key.w[sum & 3]);
    }
}

void xteaEncryptBlock(uint32_t& y, uint32_t& z, const XteaKey& key) {
    uint32_t sum = 0;
    for (int i = 0; i < kXteaRounds; ++i) {
        y += (((z << 4) ^ (z >> 5)) + z) ^ (sum + key.w[sum & 3]);
        sum += kXteaDelta;
        z += (((y << 4) ^ (y >> 5)) + y) ^ (sum + key.w[(sum >> 11) & 3]);
    }
}

void xteaDecryptBlocks(uint8_t* data, size_t len, const XteaKey& key) {
    for (size_t i = 0; i + 8 <= len; i += 8) {
        uint32_t y = rd32(data + i);
        uint32_t z = rd32(data + i + 4);
        xteaDecryptBlock(y, z, key);
        wr32(data + i, y);
        wr32(data + i + 4, z);
    }
}

void xteaEncryptBlocks(uint8_t* data, size_t len, const XteaKey& key) {
    for (size_t i = 0; i + 8 <= len; i += 8) {
        uint32_t y = rd32(data + i);
        uint32_t z = rd32(data + i + 4);
        xteaEncryptBlock(y, z, key);
        wr32(data + i, y);
        wr32(data + i + 4, z);
    }
}

Bytes xteaDecryptPadded(const uint8_t* data, size_t len, const XteaKey& key) {
    const size_t n = roundUp8(len);
    Bytes out(n, 0);
    if (data) {
        for (size_t i = 0; i < len; ++i) out[i] = data[i];
    }
    xteaDecryptBlocks(out.data(), n, key);
    return out;
}

Bytes xteaEncryptPadded(const uint8_t* data, size_t len, const XteaKey& key) {
    const size_t n = roundUp8(len);
    Bytes out(n, 0);
    if (data) {
        for (size_t i = 0; i < len; ++i) out[i] = data[i];
    }
    xteaEncryptBlocks(out.data(), n, key);
    return out;
}

}  // namespace m2
