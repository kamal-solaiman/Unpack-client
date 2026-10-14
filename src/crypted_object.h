#pragma once
#include <cstdint>
#include <vector>
#include <string>

namespace UnpackTool {

struct CryptedObjectHeader {
    uint32_t magic; // 'MCOB' or 'MCOZ' or 'MCSP' etc
    uint32_t cryptedSize;
    uint32_t compressedSize;
    uint32_t realSize;
    uint32_t cryptedMagicVerification; // usually 0x12345678 or similar, or 0 if not crypted
    // Followed by data
};

class CryptedObject {
public:
    static const uint32_t MAGIC_MCOB = 0x424F434D; // 'MCOB'
    static const uint32_t MAGIC_MCOZ = 0x5A4F434D; // 'MCOZ' LZO
    static const uint32_t MAGIC_MCSP = 0x5053434D; // 'MCSP' Snappy
    static const uint32_t MAGIC_MCOZ2 = 0x324D434F; // 'OCM2' variant?
    
    // Decrypt and decompress file content
    // Returns true if successful, outData contains decompressed data
    // key is 16-byte XTEA key as 4 uint32
    static bool Decrypt(const std::vector<uint8_t>& inData, std::vector<uint8_t>& outData, const uint32_t key[4]);
    static bool Decrypt(const uint8_t* inData, size_t inSize, std::vector<uint8_t>& outData, const uint32_t key[4]);
    
    // Check if data looks like CryptedObject
    static bool IsCryptedObject(const uint8_t* data, size_t size);
    static bool IsCryptedObject(const std::vector<uint8_t>& data);
    
    // Get info string
    static std::string GetMagicString(uint32_t magic);
};

} // namespace UnpackTool
