#pragma once
#include <cstdint>
#include <vector>
#include <cstddef>
#include <string>

namespace UnpackTool {

class XTEA {
public:
    static const uint32_t DELTA = 0x9E3779B9;
    static const uint32_t DEFAULT_ROUNDS = 32;

    // Decrypt/Encrypt single 8-byte block
    static void DecryptBlock(uint32_t v[2], const uint32_t key[4], uint32_t rounds = DEFAULT_ROUNDS);
    static void EncryptBlock(uint32_t v[2], const uint32_t key[4], uint32_t rounds = DEFAULT_ROUNDS);

    // Decrypt/Encrypt buffer (size must be multiple of 8, remainder copied as is)
    static void DecryptBuffer(uint8_t* data, size_t size, const uint32_t key[4], uint32_t rounds = DEFAULT_ROUNDS);
    static void EncryptBuffer(uint8_t* data, size_t size, const uint32_t key[4], uint32_t rounds = DEFAULT_ROUNDS);

    static void DecryptBuffer(std::vector<uint8_t>& data, const uint32_t key[4], uint32_t rounds = DEFAULT_ROUNDS);
    static void EncryptBuffer(std::vector<uint8_t>& data, const uint32_t key[4], uint32_t rounds = DEFAULT_ROUNDS);

    // Helpers to convert 16-byte key to 4 uint32 (little endian)
    static void KeyFromBytes(const uint8_t bytes[16], uint32_t key[4]);
    static void KeyToBytes(const uint32_t key[4], uint8_t bytes[16]);

    // Parse key from hex string
    static bool ParseHexKey(const std::string& hex, uint32_t key[4]);
    static std::string KeyToHex(const uint32_t key[4]);
};

} // namespace UnpackTool
