#include "xtea.h"
#include <cstring>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <cctype>

namespace UnpackTool {

void XTEA::DecryptBlock(uint32_t v[2], const uint32_t key[4], uint32_t rounds) {
    uint32_t v0 = v[0], v1 = v[1];
    uint32_t sum = DELTA * rounds;
    for (uint32_t i = 0; i < rounds; ++i) {
        v1 -= (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + key[(sum >> 11) & 3]);
        sum -= DELTA;
        v0 -= (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + key[sum & 3]);
    }
    v[0] = v0;
    v[1] = v1;
}

void XTEA::EncryptBlock(uint32_t v[2], const uint32_t key[4], uint32_t rounds) {
    uint32_t v0 = v[0], v1 = v[1];
    uint32_t sum = 0;
    for (uint32_t i = 0; i < rounds; ++i) {
        v0 += (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + key[sum & 3]);
        sum += DELTA;
        v1 += (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + key[(sum >> 11) & 3]);
    }
    v[0] = v0;
    v[1] = v1;
}

void XTEA::DecryptBuffer(uint8_t* data, size_t size, const uint32_t key[4], uint32_t rounds) {
    size_t blocks = size / 8;
    for (size_t i = 0; i < blocks; ++i) {
        uint32_t v[2];
        std::memcpy(v, data + i * 8, 8);
        DecryptBlock(v, key, rounds);
        std::memcpy(data + i * 8, v, 8);
    }
}

void XTEA::EncryptBuffer(uint8_t* data, size_t size, const uint32_t key[4], uint32_t rounds) {
    size_t blocks = size / 8;
    for (size_t i = 0; i < blocks; ++i) {
        uint32_t v[2];
        std::memcpy(v, data + i * 8, 8);
        EncryptBlock(v, key, rounds);
        std::memcpy(data + i * 8, v, 8);
    }
}

void XTEA::DecryptBuffer(std::vector<uint8_t>& data, const uint32_t key[4], uint32_t rounds) {
    if (data.empty()) return;
    DecryptBuffer(data.data(), data.size(), key, rounds);
}

void XTEA::EncryptBuffer(std::vector<uint8_t>& data, const uint32_t key[4], uint32_t rounds) {
    if (data.empty()) return;
    EncryptBuffer(data.data(), data.size(), key, rounds);
}

void XTEA::KeyFromBytes(const uint8_t bytes[16], uint32_t key[4]) {
    for (int i = 0; i < 4; ++i) {
        key[i] = (uint32_t)bytes[i * 4] |
                 ((uint32_t)bytes[i * 4 + 1] << 8) |
                 ((uint32_t)bytes[i * 4 + 2] << 16) |
                 ((uint32_t)bytes[i * 4 + 3] << 24);
    }
}

void XTEA::KeyToBytes(const uint32_t key[4], uint8_t bytes[16]) {
    for (int i = 0; i < 4; ++i) {
        bytes[i * 4] = key[i] & 0xFF;
        bytes[i * 4 + 1] = (key[i] >> 8) & 0xFF;
        bytes[i * 4 + 2] = (key[i] >> 16) & 0xFF;
        bytes[i * 4 + 3] = (key[i] >> 24) & 0xFF;
    }
}

bool XTEA::ParseHexKey(const std::string& hex, uint32_t key[4]) {
    std::string clean;
    for (char c : hex) {
        if (!std::isspace((unsigned char)c)) clean += c;
    }
    // Remove 0x prefix
    if (clean.size() >= 2 && clean[0] == '0' && (clean[1] == 'x' || clean[1] == 'X')) {
        clean = clean.substr(2);
    }
    // Must be 32 hex chars
    if (clean.size() != 32) return false;
    uint8_t bytes[16];
    for (int i = 0; i < 16; ++i) {
        std::string byteStr = clean.substr(i * 2, 2);
        try {
            bytes[i] = (uint8_t)std::stoi(byteStr, nullptr, 16);
        } catch (...) {
            return false;
        }
    }
    KeyFromBytes(bytes, key);
    return true;
}

std::string XTEA::KeyToHex(const uint32_t key[4]) {
    uint8_t bytes[16];
    KeyToBytes(key, bytes);
    std::ostringstream oss;
    oss << std::hex << std::setfill('0') << std::uppercase;
    for (int i = 0; i < 16; ++i) {
        oss << std::setw(2) << (int)bytes[i];
    }
    return oss.str();
}

} // namespace UnpackTool
