// SPDX-License-Identifier: MIT
#include "eterpack.h"

#include <cstring>
#include <map>
#include <set>

#include "crc32.h"
#include "lzo.h"
#include "snappy.h"

namespace m2 {

std::string packTypeName(uint8_t type) {
    switch (type) {
        case PACK_TYPE_RAW: return "0 (raw)";
        case PACK_TYPE_LZO: return "1 (lzo)";
        case PACK_TYPE_LZO_XTEA: return "2 (lzo+xtea)";
        case PACK_TYPE_PANAMA: return "3 (panama)";
        case PACK_TYPE_HYBRID: return "4 (hybridcrypt)";
        case PACK_TYPE_HYBRID_EXTRA: return "5 (hybridcrypt+extra)";
        case PACK_TYPE_SNAPPY_XTEA: return "6 (snappy+xtea)";
        default: return std::to_string(type) + " (unknown)";
    }
}

bool packTypeSupported(uint8_t type) { return type <= PACK_TYPE_LZO_XTEA || type == PACK_TYPE_SNAPPY_XTEA; }

namespace {

// Classic 40k layout first: it is by far the most common one.
const EntryLayout kLayouts[] = {
    {"classic-192", 192, 4, 161, 168, 172, 176, 180, 184, 4, 188},
    {"wide-offset-200", 200, 4, 161, 168, 172, 176, 180, 184, 8, 192},
    {"name256-288", 288, 4, 257, 264, 268, 272, 276, 280, 4, 284},
    {"name256-wide-296", 296, 4, 257, 264, 268, 272, 276, 280, 8, 288},
    {"name64-96", 96, 4, 65, 72, 76, 80, 84, 88, 4, 92},
};

size_t readOffset(const uint8_t* base, const EntryLayout& l) {
    return l.offsetSize == 8 ? static_cast<size_t>(rd64(base + l.offsetOff))
                             : static_cast<size_t>(rd32(base + l.offsetOff));
}

bool nameLooksValid(const std::string& n) {
    if (n.empty() || n.size() > 512) return false;
    for (unsigned char c : n) {
        if (c < 0x20 || c == 0x7F) return false;
        if (c == '*' || c == '?' || c == '"' || c == '<' || c == '>' || c == '|') return false;
    }
    return true;
}

// Picks the layout that best explains `count` entries inside `len` bytes.
const EntryLayout* detectLayout(const uint8_t* data, size_t len, uint32_t count, size_t epkSize) {
    const EntryLayout* best = nullptr;
    long long bestScore = -1;
    for (const EntryLayout& l : kLayouts) {
        long long score = 0;
        const size_t need = 12 + static_cast<size_t>(count) * l.stride;
        if (need == len) score += 1000;
        else if (need < len) score += 100;
        else continue;  // does not even fit

        if (count == 0) {
            if (score > bestScore) { bestScore = score; best = &l; }
            continue;
        }

        size_t goodNames = 0, saneOffsets = 0, saneTypes = 0, saneSizes = 0;
        const uint32_t probe = count < 64u ? count : 64u;
        for (uint32_t i = 0; i < probe; ++i) {
            const uint8_t* base = data + 12 + static_cast<size_t>(i) * l.stride;
            char name[600] = {0};
            const size_t maxName = l.nameMax < sizeof(name) - 1 ? l.nameMax : sizeof(name) - 1;
            std::memcpy(name, base + l.nameOff, maxName);
            name[maxName] = 0;
            std::string s(name);
            if (nameLooksValid(s)) ++goodNames;
            if (l.typeOff + 1 <= l.stride && base[l.typeOff] <= 6) ++saneTypes;
            if (epkSize == 0 || readOffset(base, l) < epkSize) ++saneOffsets;
            if (rd32(base + l.realSizeOff) < (1u << 30) && rd32(base + l.dataSizeOff) < (1u << 30))
                ++saneSizes;
        }
        score += static_cast<long long>(goodNames) * 8;
        score += static_cast<long long>(saneTypes) * 4;
        score += static_cast<long long>(saneOffsets) * 3;
        score += static_cast<long long>(saneSizes) * 2;
        if (l.stride == 192) score += 1;  // tie breaker towards the classic layout
        if (score > bestScore) { bestScore = score; best = &l; }
    }
    return best;
}

}  // namespace

const EntryLayout* entryLayouts(size_t& count) {
    count = sizeof(kLayouts) / sizeof(kLayouts[0]);
    return kLayouts;
}

const EntryLayout& classicLayout() { return kLayouts[0]; }

bool parseIndexBlob(const Bytes& plain, PackIndex& idx, std::string* err) {
    auto fail = [&](const std::string& m) {
        if (err) *err = m;
        return false;
    };
    if (plain.size() < 12) return fail("index: too small");
    if (rd32(plain.data()) != kMagicEPKD) return fail("index: bad magic '" + fourccName(rd32(plain.data())) + "'");
    idx.version = rd32(plain.data() + 4);
    const int32_t countSigned = static_cast<int32_t>(rd32(plain.data() + 8));
    if (idx.version != 2)
        Log::warn("index: unusual version " + std::to_string(idx.version) + " (expected 2)");
    if (countSigned < 0) return fail("index: negative file count");
    const uint32_t count = static_cast<uint32_t>(countSigned);

    const EntryLayout* layout = detectLayout(plain.data(), plain.size(), count, 0);
    if (!layout) return fail("index: cannot determine the entry layout");
    idx.layout = layout;
    Log::debug("index layout: " + std::string(layout->name) + " count=" + std::to_string(count));

    idx.entries.clear();
    idx.entries.reserve(count);
    for (uint32_t i = 0; i < count; ++i) {
        const size_t base = 12 + static_cast<size_t>(i) * layout->stride;
        if (base + layout->stride > plain.size()) {
            Log::warn("index: truncated after " + std::to_string(idx.entries.size()) + " entries");
            break;
        }
        const uint8_t* p = plain.data() + base;
        PackEntry e;
        e.id = rd32(p);
        char name[600] = {0};
        const size_t maxName = layout->nameMax < sizeof(name) - 1 ? layout->nameMax : sizeof(name) - 1;
        std::memcpy(name, p + layout->nameOff, maxName);
        name[maxName] = 0;
        e.name = name;
        e.safePath = sanitizeVirtualPath(e.name);
        e.nameCrc = rd32(p + layout->nameCrcOff);
        e.realSize = rd32(p + layout->realSizeOff);
        e.dataSize = rd32(p + layout->dataSizeOff);
        e.contentCrc = rd32(p + layout->crcOff);
        e.offset = readOffset(p, *layout);
        e.type = p[layout->typeOff];
        idx.entries.push_back(std::move(e));
    }
    return true;
}

bool loadIndexFile(const Bytes& raw, const PackKeys& keys, PackIndex& idx, std::string* err) {
    if (raw.size() < 12) {
        if (err) *err = "index: file too small";
        return false;
    }
    const uint32_t magic = rd32(raw.data());

    if (magic == kMagicEPKD) {
        idx.indexWasEncrypted = false;
        idx.containerMagic = 0;
        return parseIndexBlob(raw, idx, err);
    }

    CryptedObject co;
    std::string coErr;
    if (!parseCryptedObjectHeader(raw.data(), raw.size(), co, &coErr)) {
        // Unknown container: some servers XTEA the entire .eix (header included)
        // instead of using a Crypted Object. Try that before giving up.
        std::vector<const XteaKey*> order;
        if (keys.haveIndexKey) order.push_back(&keys.indexKey);
        if (keys.haveDataKey) order.push_back(&keys.dataKey);
        for (const XteaKey& k : keys.fallbacks) order.push_back(&k);
        std::set<std::string> seen;
        for (const XteaKey* k : order) {
            if (!seen.insert(k->toByteHex()).second) continue;
            Bytes dec = xteaDecryptPadded(raw.data(), raw.size(), *k);
            const uint32_t m = rd32(dec.data());
            if (m == kMagicEPKD) {
                Log::warn("index: unknown container '" + fourccName(magic) +
                          "', decrypted the whole file with XTEA instead");
                idx.fullFileCipher = true;
                idx.indexWasEncrypted = true;
                idx.containerMagic = 0;
                if (parseIndexBlob(dec, idx, err)) return true;
                continue;
            }
            if (m == kMagicMCOZ || m == kMagicMCSP) {
                Bytes plain;
                CryptedObject inner;
                if (parseCryptedObjectHeader(dec.data(), dec.size(), inner, nullptr) &&
                    cryptedObjectDecode(dec.data(), dec.size(), inner.encrypted() ? k : nullptr, plain,
                                        nullptr) &&
                    parseIndexBlob(plain, idx, nullptr)) {
                    Log::warn("index: whole-file XTEA in front of a '" + fourccName(m) + "' container");
                    idx.fullFileCipher = true;
                    idx.indexWasEncrypted = true;
                    idx.containerMagic = m;
                    return true;
                }
            }
        }
        if (err)
            *err = "index: " + coErr + " (first bytes: " +
                   toHex(raw.data(), raw.size() < 16 ? raw.size() : 16, " ") + ")";
        return false;
    }
    idx.indexWasEncrypted = true;
    idx.containerMagic = co.magic;

    // Ordered list of keys to try: the configured one first, then fallbacks.
    std::vector<const XteaKey*> order;
    if (keys.haveIndexKey) order.push_back(&keys.indexKey);
    if (keys.haveDataKey) order.push_back(&keys.dataKey);
    for (const XteaKey& k : keys.fallbacks) order.push_back(&k);

    if (!co.encrypted()) {
        Bytes plain;
        if (!cryptedObjectDecode(raw.data(), raw.size(), nullptr, plain, &coErr)) {
            if (err) *err = "index: " + coErr;
            return false;
        }
        return parseIndexBlob(plain, idx, err);
    }

    std::string lastErr = "index: no key available";
    std::set<std::string> seen;
    for (const XteaKey* k : order) {
        const std::string id = k->toByteHex();
        if (!seen.insert(id).second) continue;
        Bytes plain;
        if (cryptedObjectDecode(raw.data(), raw.size(), k, plain, &coErr) &&
            parseIndexBlob(plain, idx, nullptr)) {
            if (!keys.haveIndexKey || !(*k == keys.indexKey)) {
                Log::verbose("index: decrypted with a fallback key " + k->toHexArray());
            }
            idx.verifiedWithCrc = true;
            return true;
        }
        lastErr = "index: " + coErr;
    }
    if (err) *err = lastErr;
    return false;
}

namespace {

struct Strategy {
    const char* name;
    uint32_t magic;      // 0 = raw copy
    const XteaKey* key;  // null = plain container
};

bool decodeWith(const Strategy& s, const uint8_t* blob, size_t blobLen, const PackEntry& e,
                Bytes& out, std::string* err) {
    if (s.magic == 0) {
        if (blobLen != e.realSize) {
            if (err) *err = "raw size mismatch";
            return false;
        }
        out.assign(blob, blob + blobLen);
        return true;
    }
    if (rd32(blob) != s.magic) {
        if (err) *err = std::string("blob is not ") + fourccName(s.magic);
        return false;
    }
    CryptedObject co;
    std::string coErr;
    if (!parseCryptedObjectHeader(blob, blobLen, co, &coErr)) {
        if (err) *err = coErr;
        return false;
    }
    if (co.realSize != e.realSize) {
        if (err) *err = "container realSize does not match the index";
        return false;
    }
    if (co.encrypted() && !s.key) {
        if (err) *err = "container is encrypted but no key was supplied";
        return false;
    }
    // A plain container ignores the supplied key on purpose.
    return cryptedObjectDecode(blob, blobLen, co.encrypted() ? s.key : nullptr, out, err);
}

}  // namespace

bool extractEntry(const uint8_t* epk, size_t epkSize, const PackEntry& e, const PackKeys& keys,
                  bool autoDetect, Bytes& out, ExtractInfo& info, std::string* err) {
    info = ExtractInfo();
    out.clear();
    auto fail = [&](const std::string& m) {
        if (err) *err = m;
        return false;
    };
    if (!epk && epkSize != 0) return fail("no .epk data");
    if (e.offset > epkSize) return fail("entry offset past end of the .epk");
    const size_t avail = epkSize - static_cast<size_t>(e.offset);
    size_t blobLen = e.dataSize;
    if (blobLen > avail) {
        Log::verbose("    [warn] " + e.name + ": the .epk looks truncated (" +
                     std::to_string(avail) + " of " + std::to_string(e.dataSize) + " bytes available)");
        blobLen = avail;
    }
    const uint8_t* blob = epk + e.offset;

    // Strategies in the order they should be tried. The declared type comes
    // first; auto detection appends the rest.
    std::vector<Strategy> strategies;
    switch (e.type) {
        case PACK_TYPE_RAW:
            strategies.push_back({"raw", 0, nullptr});
            break;
        case PACK_TYPE_LZO:
            strategies.push_back({"lzo/plain", kMagicMCOZ, nullptr});
            strategies.push_back({"lzo/indexKey", kMagicMCOZ, keys.haveIndexKey ? &keys.indexKey : nullptr});
            break;
        case PACK_TYPE_LZO_XTEA:
            strategies.push_back({"lzo/dataKey", kMagicMCOZ, keys.haveDataKey ? &keys.dataKey : nullptr});
            strategies.push_back({"lzo/indexKey", kMagicMCOZ, keys.haveIndexKey ? &keys.indexKey : nullptr});
            break;
        case PACK_TYPE_SNAPPY_XTEA:
            strategies.push_back({"snappy/dataKey", kMagicMCSP, keys.haveDataKey ? &keys.dataKey : nullptr});
            strategies.push_back({"snappy/indexKey", kMagicMCSP, keys.haveIndexKey ? &keys.indexKey : nullptr});
            break;
        default:
            if (!autoDetect)
                return fail("unsupported pack type " + packTypeName(e.type) +
                            " (needs a server side key material)");
            break;
    }

    if (autoDetect) {
        strategies.push_back({"raw", 0, nullptr});
        strategies.push_back({"lzo/plain", kMagicMCOZ, nullptr});
        strategies.push_back({"lzo/dataKey", kMagicMCOZ, keys.haveDataKey ? &keys.dataKey : nullptr});
        strategies.push_back({"lzo/indexKey", kMagicMCOZ, keys.haveIndexKey ? &keys.indexKey : nullptr});
        strategies.push_back({"snappy/plain", kMagicMCSP, nullptr});
        strategies.push_back({"snappy/dataKey", kMagicMCSP, keys.haveDataKey ? &keys.dataKey : nullptr});
        strategies.push_back({"snappy/indexKey", kMagicMCSP, keys.haveIndexKey ? &keys.indexKey : nullptr});
        for (const XteaKey& k : keys.fallbacks) {
            strategies.push_back({"lzo/fallback", kMagicMCOZ, &k});
            strategies.push_back({"snappy/fallback", kMagicMCSP, &k});
        }
    }

    std::string lastErr = "no strategy available";
    std::set<std::string> tried;
    Bytes sizeMatched;
    std::string sizeMatchedMethod;
    bool haveSizeMatch = false;

    for (const Strategy& s : strategies) {
        const std::string tag = std::string(s.name) + "|" + (s.key ? s.key->toByteHex() : "-");
        if (!tried.insert(tag).second) continue;
        Bytes candidate;
        std::string subErr;
        if (!decodeWith(s, blob, blobLen, e, candidate, &subErr)) {
            lastErr = subErr;
            continue;
        }
        if (candidate.size() != e.realSize) {
            lastErr = "produced " + std::to_string(candidate.size()) + " bytes, expected " +
                      std::to_string(e.realSize);
            continue;
        }
        if (e.contentCrc != 0 && !crc32Matches(e.contentCrc, candidate.data(), candidate.size())) {
            // Several servers ship stale or differently computed CRCs: keep the
            // first size-correct result and keep looking for a clean one.
            lastErr = "CRC mismatch";
            if (!haveSizeMatch) {
                sizeMatched = std::move(candidate);
                sizeMatchedMethod = s.name;
                haveSizeMatch = true;
            }
            continue;
        }
        info.method = s.name;
        info.crcChecked = e.contentCrc != 0;
        info.crcOk = info.crcChecked;
        out = std::move(candidate);
        return true;
    }

    if (haveSizeMatch) {
        Log::warn(e.name + ": size is correct but the stored CRC does not match (used " +
                  sizeMatchedMethod + ")");
        info.method = sizeMatchedMethod + " (CRC mismatch)";
        info.crcChecked = true;
        info.crcOk = false;
        out = std::move(sizeMatched);
        return true;
    }

    // Last resort for auto detection: a raw entry stored with padding.
    if (autoDetect && e.realSize > 0 && blobLen >= e.realSize) {
        Bytes candidate(blob, blob + e.realSize);
        if (e.contentCrc == 0 || crc32Matches(e.contentCrc, candidate.data(), candidate.size())) {
            Log::warn(e.name + ": no container matched, took the first " +
                      std::to_string(e.realSize) + " raw bytes");
            info.method = "raw/prefix (last resort)";
            info.crcChecked = e.contentCrc != 0;
            info.crcOk = info.crcChecked;
            out = std::move(candidate);
            return true;
        }
    }
    return fail(lastErr);
}

}  // namespace m2
