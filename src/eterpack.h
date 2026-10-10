// SPDX-License-Identifier: MIT
// EterPack (.eix index + .epk content) reader.
#pragma once

#include <cstdint>
#include <string>
#include <vector>

#include "crypted_object.h"
#include "util.h"
#include "xtea.h"

namespace m2 {

// Entry "compressed_type" values used by the client.
enum PackType : uint8_t {
    PACK_TYPE_RAW = 0,
    PACK_TYPE_LZO = 1,
    PACK_TYPE_LZO_XTEA = 2,
    PACK_TYPE_PANAMA = 3,
    PACK_TYPE_HYBRID = 4,
    PACK_TYPE_HYBRID_EXTRA = 5,
    PACK_TYPE_SNAPPY_XTEA = 6,
};
std::string packTypeName(uint8_t type);
bool packTypeSupported(uint8_t type);

// Keys used by a pack: the index key protects the .eix, the data key protects
// the encrypted entries inside the .epk.
struct PackKeys {
    XteaKey indexKey{};
    XteaKey dataKey{};
    bool haveIndexKey = false;
    bool haveDataKey = false;
    // Extra keys collected along the way (known defaults, scan hits) that can
    // be tried when auto detection is on.
    std::vector<XteaKey> fallbacks;
};

// Different client revisions pad the index entry differently. The classic
// layout is 192 bytes; the table below lets the tool adapt instead of failing.
struct EntryLayout {
    const char* name;
    size_t stride;
    size_t nameOff;
    size_t nameMax;      // bytes available for the NUL terminated name
    size_t nameCrcOff;
    size_t realSizeOff;
    size_t dataSizeOff;
    size_t crcOff;
    size_t offsetOff;
    size_t offsetSize;   // 4 or 8
    size_t typeOff;
};
const EntryLayout* entryLayouts(size_t& count);
const EntryLayout& classicLayout();

struct PackEntry {
    uint32_t id = 0;
    std::string name;      // exactly as stored in the index
    std::string safePath;  // sanitised, ready to be written below the out dir
    uint32_t nameCrc = 0;
    uint32_t realSize = 0;
    uint32_t dataSize = 0;
    uint32_t contentCrc = 0;
    uint64_t offset = 0;
    uint8_t type = 0;
};

struct PackIndex {
    uint32_t version = 0;
    const EntryLayout* layout = nullptr;
    bool indexWasEncrypted = false;
    // Some servers XTEA the whole .eix instead of using a Crypted Object.
    bool fullFileCipher = false;
    uint32_t containerMagic = 0;
    bool verifiedWithCrc = false;
    std::vector<PackEntry> entries;
};

// Parses a decrypted 'EPKD' blob.
bool parseIndexBlob(const Bytes& plain, PackIndex& idx, std::string* err = nullptr);

// Reads a .eix file: handles a plain 'EPKD' file as well as an MCOZ/MCSP
// wrapped (and possibly XTEA encrypted) one.
bool loadIndexFile(const Bytes& raw, const PackKeys& keys, PackIndex& idx, std::string* err = nullptr);

struct ExtractInfo {
    std::string method;   // human readable description of what worked
    bool crcOk = false;
    bool crcChecked = false;
};

// Pulls one entry out of the .epk image. When `autoDetect` is set and the
// declared type fails, every supported container/key combination is tried and
// the one that produces the right size (and CRC) wins.
bool extractEntry(const uint8_t* epk, size_t epkSize, const PackEntry& e, const PackKeys& keys,
                  bool autoDetect, Bytes& out, ExtractInfo& info, std::string* err = nullptr);

}  // namespace m2
