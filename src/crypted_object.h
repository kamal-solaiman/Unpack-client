// SPDX-License-Identifier: MIT
// The "Crypted Object" container Metin2 wraps index files and pack entries in:
//
//   offset  size  field
//   0       4     magic        'MCOZ' (LZO) or 'MCSP' (Snappy)
//   4       4     encryptSize  size of the XTEA encrypted region, 0 = plain
//   8       4     compressedSize
//   12      4     realSize     size of the decompressed payload
//   16      4     verification plain magic, or the first dword of the cipher
//   20      ...   payload
//
// When encryptSize > 0 the encrypted region starts at offset 16 and holds
// [verification magic][compressed data] padded up to a multiple of 8 bytes.
#pragma once

#include <cstdint>
#include <string>

#include "util.h"
#include "xtea.h"

namespace m2 {

uint32_t fourcc(const char s[4]);
std::string fourccName(uint32_t v);

constexpr uint32_t kMagicMCOZ = 0x5A4F434Du;  // 'MCOZ'
constexpr uint32_t kMagicMCSP = 0x5053434Du;  // 'MCSP'
constexpr uint32_t kMagicEPKD = 0x444B5045u;  // 'EPKD'
constexpr uint32_t kMagicMMPT = 0x54504D4Du;  // 'MMPT'
constexpr uint32_t kMagicMIPX = 0x5850494Du;  // 'MIPX'

struct CryptedObject {
    uint32_t magic = 0;
    uint32_t encryptSize = 0;
    uint32_t compressedSize = 0;
    uint32_t realSize = 0;

    bool encrypted() const { return encryptSize > 0; }
    // Offset of the compressed stream once the container is in plain form.
    size_t plainPayloadOffset() const { return encrypted() ? 4 : 20; }
    bool isLzo() const { return magic == kMagicMCOZ; }
    bool isSnappy() const { return magic == kMagicMCSP; }
};

// Reads the 16 byte header. `len` must be at least 16.
bool parseCryptedObjectHeader(const uint8_t* data, size_t len, CryptedObject& co,
                              std::string* err = nullptr);

// Fast key check used while brute forcing: decrypts a single 8 byte block at
// offset 16 and compares the verification dword with the container magic.
// ~1 in 4 billion false positives, which is enough to short list candidates.
bool cryptedObjectKeyLooksRight(const uint8_t* data, size_t len, const XteaKey& key,
                                const CryptedObject& co);

// Full decode: XTEA decrypt (when needed) + LZO/Snappy inflate.
// `key` may be null for unencrypted containers.
bool cryptedObjectDecode(const uint8_t* data, size_t len, const XteaKey* key, Bytes& out,
                         std::string* err = nullptr);

// Inverse of the above, used by the test suite (and by any future repacker).
// Compression is "stored" (valid stream, no size gain).
bool cryptedObjectEncode(const Bytes& plain, const XteaKey* key, uint32_t magic, Bytes& out,
                         std::string* err = nullptr);

}  // namespace m2
