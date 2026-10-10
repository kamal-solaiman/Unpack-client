// SPDX-License-Identifier: MIT
#include "crypted_object.h"

#include <cstring>

#include "lzo.h"
#include "snappy.h"

namespace m2 {

uint32_t fourcc(const char s[4]) {
    return static_cast<uint32_t>(static_cast<uint8_t>(s[0])) |
           (static_cast<uint32_t>(static_cast<uint8_t>(s[1])) << 8) |
           (static_cast<uint32_t>(static_cast<uint8_t>(s[2])) << 16) |
           (static_cast<uint32_t>(static_cast<uint8_t>(s[3])) << 24);
}

std::string fourccName(uint32_t v) {
    char buf[5] = {0, 0, 0, 0, 0};
    for (int i = 0; i < 4; ++i) {
        uint8_t c = static_cast<uint8_t>((v >> (8 * i)) & 0xFF);
        buf[i] = (c >= 0x20 && c < 0x7F) ? static_cast<char>(c) : '?';
    }
    return buf;
}

bool parseCryptedObjectHeader(const uint8_t* data, size_t len, CryptedObject& co, std::string* err) {
    auto fail = [&](const std::string& what) {
        if (err) *err = what;
        return false;
    };
    if (!data || len < 16) return fail("crypted object: file too small");
    co.magic = rd32(data);
    co.encryptSize = rd32(data + 4);
    co.compressedSize = rd32(data + 8);
    co.realSize = rd32(data + 12);
    if (co.magic != kMagicMCOZ && co.magic != kMagicMCSP)
        return fail("crypted object: unknown magic " + fourccName(co.magic));
    if (co.encrypted()) {
        if (16 + co.encryptSize > len) return fail("crypted object: encrypted region past end of file");
        if (co.encryptSize < co.compressedSize) return fail("crypted object: inconsistent sizes");
    } else {
        if (len < 20) return fail("crypted object: file too small");
        if (rd32(data + 16) != co.magic) return fail("crypted object: verification magic mismatch");
        if (20 + co.compressedSize > len) return fail("crypted object: payload past end of file");
    }
    return true;
}

bool cryptedObjectKeyLooksRight(const uint8_t* data, size_t len, const XteaKey& key,
                                const CryptedObject& co) {
    if (!co.encrypted()) return true;
    if (len < 24) return false;
    // One block is enough: it decrypts the verification dword.
    uint32_t y = rd32(data + 16);
    uint32_t z = rd32(data + 20);
    xteaDecryptBlock(y, z, key);
    return y == co.magic;
}

bool cryptedObjectDecode(const uint8_t* data, size_t len, const XteaKey* key, Bytes& out,
                         std::string* err) {
    out.clear();
    CryptedObject co;
    if (!parseCryptedObjectHeader(data, len, co, err)) return false;

    const uint8_t* compressed = nullptr;
    Bytes decrypted;
    if (co.encrypted()) {
        if (!key) {
            if (err) *err = "crypted object: an XTEA key is required";
            return false;
        }
        decrypted = xteaDecryptPadded(data + 16, co.encryptSize, *key);
        if (rd32(decrypted.data()) != co.magic) {
            if (err) *err = "crypted object: wrong XTEA key";
            return false;
        }
        if (4 + co.compressedSize > decrypted.size()) {
            if (err) *err = "crypted object: decrypted buffer too short";
            return false;
        }
        compressed = decrypted.data() + 4;
    } else {
        compressed = data + 20;
    }

    std::string subErr;
    bool ok = false;
    if (co.isLzo())
        ok = lzo1xDecompressTo(compressed, co.compressedSize, co.realSize, out, &subErr);
    else
        ok = snappyDecompressTo(compressed, co.compressedSize, co.realSize, out, &subErr);

    if (!ok) {
        if (err) *err = "crypted object: " + subErr;
        out.clear();
        return false;
    }
    if (out.size() != co.realSize) {
        if (err) *err = "crypted object: decompressed " + std::to_string(out.size()) +
                        " bytes, expected " + std::to_string(co.realSize);
        out.clear();
        return false;
    }
    return true;
}

bool cryptedObjectEncode(const Bytes& plain, const XteaKey* key, uint32_t magic, Bytes& out,
                         std::string* err) {
    out.clear();
    Bytes compressed;
    if (magic == kMagicMCOZ) {
        if (!lzo1xStore(plain.data(), plain.size(), compressed)) {
            if (err) *err = "cannot store an empty payload as LZO";
            return false;
        }
    } else if (magic == kMagicMCSP) {
        if (!snappyStore(plain.data(), plain.size(), compressed)) {
            if (err) *err = "snappy store failed";
            return false;
        }
    } else {
        if (err) *err = "crypted object: unsupported magic";
        return false;
    }

    uint8_t header[16];
    wr32(header, magic);
    wr32(header + 8, static_cast<uint32_t>(compressed.size()));
    wr32(header + 12, static_cast<uint32_t>(plain.size()));

    if (key) {
        Bytes body;
        body.reserve(4 + compressed.size());
        uint8_t verif[4];
        wr32(verif, magic);
        body.insert(body.end(), verif, verif + 4);
        body.insert(body.end(), compressed.begin(), compressed.end());
        Bytes enc = xteaEncryptPadded(body.data(), body.size(), *key);
        wr32(header + 4, static_cast<uint32_t>(enc.size()));
        out.insert(out.end(), header, header + 16);
        out.insert(out.end(), enc.begin(), enc.end());
    } else {
        wr32(header + 4, 0);
        uint8_t verif[4];
        wr32(verif, magic);
        out.insert(out.end(), header, header + 16);
        out.insert(out.end(), verif, verif + 4);
        out.insert(out.end(), compressed.begin(), compressed.end());
    }
    return true;
}

}  // namespace m2
