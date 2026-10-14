#include "crypted_object.h"
#include "xtea.h"
#include <cstring>
#include <iostream>

extern "C" {
#include "lzo/minilzo.h"
}

// Minimal Snappy decompression
namespace Snappy {
    // Very small snappy decompressor implementation
    // Based on snappy format description
    static bool ReadVarint(const uint8_t** ip, const uint8_t* ip_limit, uint32_t* result) {
        const uint8_t* p = *ip;
        uint32_t res = 0;
        int shift = 0;
        while (p < ip_limit && shift < 32) {
            uint8_t b = *p++;
            res |= (b & 0x7F) << shift;
            if ((b & 0x80) == 0) {
                *result = res;
                *ip = p;
                return true;
            }
            shift += 7;
        }
        return false;
    }

    static bool Decompress(const uint8_t* src, size_t src_len, std::vector<uint8_t>& dst) {
        const uint8_t* ip = src;
        const uint8_t* ip_limit = src + src_len;
        uint32_t uncompressed_len = 0;
        if (!ReadVarint(&ip, ip_limit, &uncompressed_len)) return false;
        
        dst.resize(uncompressed_len);
        uint8_t* op = dst.data();
        uint8_t* op_limit = op + uncompressed_len;

        while (ip < ip_limit && op < op_limit) {
            uint8_t tag = *ip++;
            uint32_t length = 0;
            uint32_t offset = 0;

            if ((tag & 0x03) == 0) { // Literal
                length = (tag >> 2) + 1;
                if (length > 60) {
                    // Long literal
                    int bytes = length - 60;
                    if (ip + bytes > ip_limit) return false;
                    length = 0;
                    for (int i = 0; i < bytes; ++i) {
                        length |= ((uint32_t)ip[i]) << (i * 8);
                    }
                    ip += bytes;
                    length++;
                }
                if (ip + length > ip_limit || op + length > op_limit) return false;
                std::memcpy(op, ip, length);
                ip += length;
                op += length;
            } else {
                // Copy
                if ((tag & 0x03) == 1) {
                    length = ((tag >> 2) & 0x07) + 4;
                    offset = ((tag >> 5) << 8) + *ip++ + 1;
                } else if ((tag & 0x03) == 2) {
                    length = (tag >> 2) + 1;
                    if (ip + 2 > ip_limit) return false;
                    offset = ip[0] | (ip[1] << 8);
                    offset++;
                    ip += 2;
                } else { // 3
                    length = (tag >> 2) + 1;
                    if (ip + 4 > ip_limit) return false;
                    offset = ip[0] | (ip[1] << 8) | (ip[2] << 16) | (ip[3] << 24);
                    offset++;
                    ip += 4;
                }
                if (offset > (uint32_t)(op - dst.data()) || op + length > op_limit) return false;
                // Copy with overlap handling
                uint8_t* from = op - offset;
                for (uint32_t i = 0; i < length; ++i) {
                    *op++ = *from++;
                }
            }
        }
        return op == op_limit && ip == ip_limit;
    }
}

namespace UnpackTool {

bool CryptedObject::IsCryptedObject(const uint8_t* data, size_t size) {
    if (size < sizeof(CryptedObjectHeader)) return false;
    uint32_t magic;
    std::memcpy(&magic, data, 4);
    return magic == MAGIC_MCOB || magic == MAGIC_MCOZ || magic == MAGIC_MCSP;
}

bool CryptedObject::IsCryptedObject(const std::vector<uint8_t>& data) {
    return IsCryptedObject(data.data(), data.size());
}

std::string CryptedObject::GetMagicString(uint32_t magic) {
    char buf[5];
    std::memcpy(buf, &magic, 4);
    buf[4] = '\0';
    return std::string(buf, 4);
}

bool CryptedObject::Decrypt(const std::vector<uint8_t>& inData, std::vector<uint8_t>& outData, const uint32_t key[4]) {
    return Decrypt(inData.data(), inData.size(), outData, key);
}

bool CryptedObject::Decrypt(const uint8_t* inData, size_t inSize, std::vector<uint8_t>& outData, const uint32_t key[4]) {
    if (inSize < sizeof(CryptedObjectHeader)) {
        // Not crypted object, try raw XTEA decrypt?
        return false;
    }

    CryptedObjectHeader hdr;
    std::memcpy(&hdr, inData, sizeof(hdr));

    // Check magic
    if (hdr.magic != MAGIC_MCOB && hdr.magic != MAGIC_MCOZ && hdr.magic != MAGIC_MCSP) {
        // Not a crypted object, maybe raw file that is XTEA encrypted without header?
        // Try to decrypt as raw XTEA if size is multiple of 8
        return false;
    }

    size_t headerSize = sizeof(CryptedObjectHeader);
    if (inSize < headerSize) return false;

    size_t dataOffset = headerSize;
    size_t dataSize = inSize - headerSize;

    // If cryptedSize == 0, not encrypted
    std::vector<uint8_t> cryptedData;
    if (hdr.cryptedSize == 0) {
        cryptedData.assign(inData + dataOffset, inData + inSize);
    } else {
        if (hdr.cryptedSize > dataSize) {
            // Corrupt
            return false;
        }
        cryptedData.assign(inData + dataOffset, inData + dataOffset + hdr.cryptedSize);
        // Decrypt
        XTEA::DecryptBuffer(cryptedData, key);
    }

    // Now cryptedData should be either compressed or raw
    if (hdr.magic == MAGIC_MCOB) {
        // Raw, no compression
        outData = cryptedData;
        if (hdr.realSize != 0 && outData.size() > hdr.realSize) {
            outData.resize(hdr.realSize);
        }
        return true;
    } else if (hdr.magic == MAGIC_MCOZ) {
        // LZO compressed
        if (hdr.compressedSize == 0) {
            outData = cryptedData;
            return true;
        }
        // LZO decompress
        if (lzo_init() != LZO_E_OK) {
            std::cerr << "[ERROR] LZO init failed\n";
            return false;
        }
        lzo_uint outLen = hdr.realSize;
        if (outLen == 0) {
            // Estimate
            outLen = cryptedData.size() * 4 + 1024;
        }
        outData.resize(outLen);
        lzo_uint inLen = hdr.compressedSize;
        if (inLen == 0) inLen = cryptedData.size();
        if (inLen > cryptedData.size()) inLen = cryptedData.size();

        int r = lzo1x_decompress_safe(cryptedData.data(), inLen, outData.data(), &outLen, nullptr);
        if (r != LZO_E_OK) {
            // Try without safe
            outLen = outData.size();
            r = lzo1x_decompress(cryptedData.data(), inLen, outData.data(), &outLen, nullptr);
        }
        if (r != LZO_E_OK) {
            std::cerr << "[ERROR] LZO decompress failed: " << r << " inLen=" << inLen << " outLen=" << outLen << "\n";
            return false;
        }
        outData.resize(outLen);
        return true;
    } else if (hdr.magic == MAGIC_MCSP) {
        // Snappy compressed
        if (!Snappy::Decompress(cryptedData.data(), cryptedData.size(), outData)) {
            std::cerr << "[ERROR] Snappy decompress failed\n";
            // Fallback: return crypted data
            outData = cryptedData;
            return false;
        }
        return true;
    }

    return false;
}

} // namespace UnpackTool
