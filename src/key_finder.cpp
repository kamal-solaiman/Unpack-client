// SPDX-License-Identifier: MIT
#include "key_finder.h"

#include <algorithm>
#include <cctype>
#include <cstring>
#include <unordered_set>

#include "crc32.h"

namespace m2 {
namespace {

constexpr uint32_t kImmediateWindow = 96;  // max byte distance between 4 key loads

uint64_t mixKey(const XteaKey& k) {
    uint64_t h = 0x9E3779B97F4A7C15ull;
    for (int i = 0; i < 4; ++i) {
        h ^= k.w[i];
        h *= 0x100000001B3ull;
        h ^= h >> 29;
    }
    return h;
}

bool isInteresting(const XteaKey& k) {
    if (k.isZero()) return false;
    // Reject keys made of four identical dwords and of all-same bytes: they are
    // padding, never a real key.
    if (k.w[0] == k.w[1] && k.w[1] == k.w[2] && k.w[2] == k.w[3]) {
        const uint8_t b0 = static_cast<uint8_t>(k.w[0] & 0xFF);
        bool same = true;
        for (int i = 0; i < 4; ++i) {
            uint32_t v = k.w[i];
            for (int j = 0; j < 4; ++j)
                if (static_cast<uint8_t>((v >> (8 * j)) & 0xFF) != b0) same = false;
        }
        if (same) return false;
    }
    return true;
}

struct CandidateSink {
    std::vector<KeyHit>* out;
    std::unordered_set<uint64_t> seen;

    bool add(const KeyHit& hit) {
        if (!isInteresting(hit.key)) return false;
        if (!seen.insert(mixKey(hit.key)).second) return false;
        out->push_back(hit);
        return true;
    }
};

struct Immediate {
    uint64_t offset;
    uint32_t value;
};

// Collects `imm32` operands of the instructions a compiler normally uses to
// materialise a static key array (push imm32 / mov r32, imm32 / mov [m], imm32).
void collectImmediates(const uint8_t* base, size_t len, uint64_t fileOffset,
                       std::vector<Immediate>& out) {
    for (size_t i = 0; i + 5 <= len;) {
        const uint8_t op = base[i];
        if (op == 0x68) {  // push imm32
            out.push_back({fileOffset + i, rd32(base + i + 1)});
            i += 5;
            continue;
        }
        if (op >= 0xB8 && op <= 0xBF) {  // mov r32, imm32
            out.push_back({fileOffset + i, rd32(base + i + 1)});
            i += 5;
            continue;
        }
        if (op == 0xC7 && i + 6 <= len) {  // mov r/m32, imm32
            const uint8_t modrm = base[i + 1];
            if (((modrm >> 3) & 7) != 0) {  // not the /0 extension
                ++i;
                continue;
            }
            const uint8_t mod = modrm >> 6;
            const uint8_t rm = modrm & 7;
            size_t immPos = i + 2;  // right after opcode + modrm
            if (mod == 0) {
                if (rm == 4) immPos += 1;        // SIB
                else if (rm == 5) immPos += 4;   // disp32 with no base register
            } else if (mod == 1) {
                immPos += 1;                     // disp8
                if (rm == 4) immPos += 1;        // SIB
            } else if (mod == 2) {
                immPos += 4;                     // disp32
                if (rm == 4) immPos += 1;        // SIB
            }
            if (immPos + 4 > len) break;
            out.push_back({fileOffset + immPos, rd32(base + immPos)});
            i = immPos + 4;
            continue;
        }
        ++i;
    }
}

std::vector<size_t> permutations4() {
    std::vector<size_t> idx = {0, 1, 2, 3};
    std::vector<size_t> perms;
    perms.reserve(24 * 4);
    std::sort(idx.begin(), idx.end());
    do {
        for (size_t v : idx) perms.push_back(v);
    } while (std::next_permutation(idx.begin(), idx.end()));
    return perms;
}

// Scans printable runs that could be a key expressed as text ("A1B2..." or a
// 16 char passphrase).
void collectStringKeys(const uint8_t* base, size_t len, uint64_t fileOffset, CandidateSink& sink) {
    size_t i = 0;
    while (i < len) {
        if (base[i] < 0x20 || base[i] >= 0x7F) {
            ++i;
            continue;
        }
        size_t j = i;
        while (j < len && base[j] >= 0x20 && base[j] < 0x7F) ++j;
        const size_t run = j - i;
        if (run >= 16 && run <= 128) {
            std::string s(reinterpret_cast<const char*>(base + i), run);
            Bytes bytes;
            if (run == 32 || run == 34) {  // hex string, maybe with 0x
                std::string hexOnly;
                for (char c : s)
                    if (std::isxdigit(static_cast<unsigned char>(c))) hexOnly += c;
                if (hexOnly.size() == 32) {
                    auto parsed = fromHex(hexOnly);
                    if (parsed && parsed->size() == 16) bytes = *parsed;
                }
            }
            if (bytes.empty()) {
                bytes.assign(base + i, base + i + 16);
            }
            if (bytes.size() == 16) {
                KeyHit hit;
                hit.key = XteaKey::fromBytes(bytes.data());
                hit.fileOffset = fileOffset + i;
                hit.region = "data";
                hit.method = "ascii-string";
                sink.add(hit);
            }
        }
        i = j + 1;
    }
}

void scanRegionAligned(const uint8_t* base, size_t len, uint64_t fileOffset, const std::string& region,
                       const char* method, size_t step, CandidateSink& sink) {
    if (len < 16) return;
    for (size_t off = 0; off + 16 <= len; off += step) {
        KeyHit hit;
        hit.key = XteaKey::fromBytes(base + off);
        hit.fileOffset = fileOffset + off;
        hit.region = region;
        hit.method = method;
        sink.add(hit);
    }
}

std::vector<size_t> findBytes(const uint8_t* hay, size_t hayLen, const uint8_t* needle, size_t nLen) {
    std::vector<size_t> hits;
    if (nLen == 0 || hayLen < nLen) return hits;
    for (size_t i = 0; i + nLen <= hayLen; ++i)
        if (hay[i] == needle[0] && std::memcmp(hay + i, needle, nLen) == 0) hits.push_back(i);
    return hits;
}

}  // namespace

const KnownKey* knownKeys(size_t& count) {
    static const KnownKey kKeys[] = {
        {"EterPack index (.eix)", {0x02B09EB9u, 0x0581696Fu, 0x289B9863u, 0x001A1879u}},
        {"EterPack content (.epk)", {0x04B4B822u, 0x1F6EB264u, 0x0018EAAEu, 0x1CFBF6A6u}},
        {"item_proto", {0x0002A4A1u, 0x045415AAu, 0x185A8BE7u, 0x01AAD6ABu}},
        {"mob_proto", {0x00497446u, 0x00004A0Bu, 0x00086EB7u, 0x0068189Du}},
    };
    count = sizeof(kKeys) / sizeof(kKeys[0]);
    return kKeys;
}

int scoreKeyPlausibility(const XteaKey& k) {
    Bytes b = k.toBytes();
    int score = 0;
    std::vector<int> hist(256, 0);
    int zeros = 0;
    for (uint8_t v : b) {
        hist[v]++;
        if (v == 0) zeros++;
        if (v >= 0x20 && v < 0x7F) score -= 1;  // printable bytes are suspicious
    }
    int distinct = 0;
    for (int c : hist)
        if (c) distinct++;
    score += distinct * 3;
    if (zeros == 0) score += 10;
    else if (zeros <= 2) score += 4;
    else score -= zeros * 2;
    for (int i = 0; i < 4; ++i) {
        const uint32_t v = k.w[i];
        if (v > 0x00FFFFFF && v < 0xFF000000) score += 2;  // looks like a random dword
        if (v == 0 || v == 0xFFFFFFFFu) score -= 8;
    }
    return score;
}

void collectKeyCandidates(const Bytes& image, const PeImage* pe, const KeyScanOptions& opt,
                          std::vector<KeyHit>& out) {
    out.clear();
    CandidateSink sink{&out, {}};

    if (opt.includeKnown) {
        size_t n = 0;
        const KnownKey* kk = knownKeys(n);
        for (size_t i = 0; i < n; ++i) {
            KeyHit hit;
            for (int j = 0; j < 4; ++j) hit.key.w[j] = kk[i].w[j];
            hit.region = "known";
            hit.method = std::string("known-default: ") + kk[i].what;
            sink.add(hit);
        }
    }

    struct Region {
        const uint8_t* base;
        size_t len;
        uint64_t fileOffset;
        std::string name;
        bool code;
    };
    std::vector<Region> dataRegions, codeRegions;
    if (pe && pe->valid) {
        for (const PeSection& s : pe->sections) {
            if (!s.readable() || s.rawSize < 16) continue;
            if (s.rawPtr + s.rawSize > image.size()) continue;
            Region r{image.data() + s.rawPtr, s.rawSize, s.rawPtr, s.name,
                     s.executable() || (s.characteristics & kScnCntCode) != 0};
            if (r.code) codeRegions.push_back(r);
            else dataRegions.push_back(r);
        }
        // Bigger data sections first: that is where a static key array lives.
        std::sort(dataRegions.begin(), dataRegions.end(),
                  [](const Region& a, const Region& b) { return a.len > b.len; });
    } else {
        dataRegions.push_back({image.data(), image.size(), 0, "file", false});
    }

    if (opt.scanData) {
        for (const Region& r : dataRegions) {
            scanRegionAligned(r.base, r.len, r.fileOffset, r.name, "data-aligned", 4, sink);
            collectStringKeys(r.base, r.len, r.fileOffset, sink);
        }
    }

    std::vector<Immediate> imms;
    if (opt.scanCode) {
        for (const Region& r : codeRegions) collectImmediates(r.base, r.len, r.fileOffset, imms);
        if (imms.empty()) {
            // Not a PE, or no code section detected: treat the whole image as code.
            collectImmediates(image.data(), image.size(), 0, imms);
        }
        const std::vector<size_t> perms = opt.unaligned ? permutations4() : std::vector<size_t>{0, 1, 2, 3};
        size_t windows = 0;
        for (size_t i = 0; i + 3 < imms.size(); ++i) {
            if (imms[i + 3].offset - imms[i].offset > kImmediateWindow) continue;
            if (++windows > 200000) break;
            uint32_t v[4] = {imms[i].value, imms[i + 1].value, imms[i + 2].value, imms[i + 3].value};
            for (size_t p = 0; p + 3 < perms.size(); p += 4) {
                KeyHit hit;
                for (int j = 0; j < 4; ++j) hit.key.w[j] = v[perms[p + j]];
                hit.fileOffset = imms[i].offset;
                hit.region = "code";
                hit.method = "text-immediates";
                if (sink.add(hit) && opt.maxCandidates && out.size() >= opt.maxCandidates) return;
            }
        }
        for (const Region& r : codeRegions) {
            scanRegionAligned(r.base, r.len, r.fileOffset, r.name, "code-aligned", 4, sink);
            if (opt.maxCandidates && out.size() >= opt.maxCandidates) return;
        }
    }

    if (opt.unaligned) {
        scanRegionAligned(image.data(), image.size(), 0, "file", "deep-unaligned", 1, sink);
    }

    if (opt.maxCandidates && out.size() > opt.maxCandidates) out.resize(opt.maxCandidates);
}

void collectAdjacentKeyPairs(const Bytes& image, const PeImage* pe, std::vector<KeyHit>& out,
                             size_t limit) {
    out.clear();
    std::vector<std::pair<size_t, size_t>> spans;  // (file offset, length)
    if (pe && pe->valid) {
        for (const PeSection& sec : pe->sections) {
            if (!sec.readable() || sec.executable()) continue;
            if (sec.rawPtr + sec.rawSize > image.size()) continue;
            spans.push_back({sec.rawPtr, sec.rawSize});
        }
    }
    if (spans.empty()) spans.push_back({0, image.size()});
    for (size_t r = 0; r < spans.size(); ++r) {
        const uint8_t* base = image.data();
        const size_t start = spans[r].first, len = spans[r].second;
        for (size_t off = 0; off + 32 <= len; off += 4) {
            KeyHit a, b;
            a.key = XteaKey::fromBytes(base + start + off);
            b.key = XteaKey::fromBytes(base + start + off + 16);
            if (!isInteresting(a.key) || !isInteresting(b.key)) continue;
            const int sa = scoreKeyPlausibility(a.key), sb = scoreKeyPlausibility(b.key);
            if (sa < 12 || sb < 12) continue;
            a.fileOffset = start + off;
            b.fileOffset = start + off + 16;
            a.score = sa + sb;
            b.score = sa + sb;
            a.method = "adjacent-pair(first)";
            b.method = "adjacent-pair(second)";
            out.push_back(a);
            out.push_back(b);
            if (out.size() >= limit * 2) return;
        }
    }
    std::stable_sort(out.begin(), out.end(),
                     [](const KeyHit& x, const KeyHit& y) { return x.score > y.score; });
    if (out.size() > limit * 2) out.resize(limit * 2);
}

bool quickCheckContainer(const uint8_t* data, size_t len, const XteaKey& key, uint32_t expectedMagic) {
    if (len < 24) return false;
    uint32_t y = rd32(data + 16);
    uint32_t z = rd32(data + 20);
    xteaDecryptBlock(y, z, key);
    return y == expectedMagic;
}

bool verifyIndexKey(const Bytes& eix, const XteaKey& key, PackIndex* idx, std::string* err) {
    if (eix.size() < 20) {
        if (err) *err = "index too small";
        return false;
    }
    const uint32_t magic = rd32(eix.data());
    if (magic == kMagicEPKD) return true;  // plain index, no key needed

    CryptedObject co;
    std::string coErr;
    if (!parseCryptedObjectHeader(eix.data(), eix.size(), co, &coErr)) {
        // Not a Crypted Object: some servers XTEA the whole .eix, header
        // included. Decrypt everything and look for a known magic.
        const Bytes dec = xteaDecryptPadded(eix.data(), eix.size(), key);
        const uint32_t m = rd32(dec.data());
        PackIndex local;
        if (m == kMagicEPKD && parseIndexBlob(dec, local, nullptr)) {
            if (idx) *idx = std::move(local);
            return true;
        }
        if (m == kMagicMCOZ || m == kMagicMCSP) {
            CryptedObject inner;
            Bytes plain;
            if (parseCryptedObjectHeader(dec.data(), dec.size(), inner, nullptr) &&
                cryptedObjectDecode(dec.data(), dec.size(), inner.encrypted() ? &key : nullptr, plain,
                                    nullptr) &&
                parseIndexBlob(plain, local, nullptr)) {
                if (idx) *idx = std::move(local);
                return true;
            }
        }
        if (err) *err = coErr;
        return false;
    }
    if (!co.encrypted()) return true;
    if (!quickCheckContainer(eix.data(), eix.size(), key, co.magic)) {
        if (err) *err = "verification magic mismatch";
        return false;
    }
    Bytes plain;
    if (!cryptedObjectDecode(eix.data(), eix.size(), &key, plain, &coErr)) {
        if (err) *err = coErr;
        return false;
    }
    PackIndex local;
    if (!parseIndexBlob(plain, local, &coErr)) {
        if (err) *err = coErr;
        return false;
    }
    if (idx) *idx = std::move(local);
    return true;
}

bool verifyDataKey(const uint8_t* blob, size_t len, const XteaKey& key, uint32_t expectedRealSize,
                   uint32_t expectedCrc, std::string* err) {
    CryptedObject co;
    std::string coErr;
    if (!parseCryptedObjectHeader(blob, len, co, &coErr)) {
        if (err) *err = coErr;
        return false;
    }
    if (!co.encrypted()) return true;
    if (!quickCheckContainer(blob, len, key, co.magic)) {
        if (err) *err = "verification magic mismatch";
        return false;
    }
    Bytes plain;
    if (!cryptedObjectDecode(blob, len, &key, plain, &coErr)) {
        if (err) *err = coErr;
        return false;
    }
    if (expectedRealSize && plain.size() != expectedRealSize) {
        if (err) *err = "size mismatch";
        return false;
    }
    if (expectedCrc && !crc32Matches(expectedCrc, plain.data(), plain.size())) {
        if (err) *err = "CRC mismatch";
        return false;
    }
    return true;
}

KeySearchResult searchKeys(const Bytes& image, const KeyScanOptions& opt, const Bytes& eix,
                           const uint8_t* epk, size_t epkSize, const ProgressFn& progress) {
    KeySearchResult res;

    PeImage pe;
    std::string peErr;
    const bool peOk = parsePe(image.data(), image.size(), pe, &peErr);

    std::vector<KeyHit> candidates;
    collectKeyCandidates(image, peOk ? &pe : nullptr, opt, candidates);

    if (peOk)
        res.message = "PE parsed: " + std::to_string(pe.sections.size()) + " sections, " +
                      std::to_string(candidates.size()) + " candidate keys";
    else
        res.message = "PE header not usable (" + peErr + "), scanned the raw file: " +
                      std::to_string(candidates.size()) + " candidates";

    // Which stock keys are physically present in the image? Useful signal even
    // when the pack uses different ones.
    size_t nk = 0;
    const KnownKey* kk = knownKeys(nk);
    for (size_t i = 0; i < nk; ++i) {
        XteaKey k;
        for (int j = 0; j < 4; ++j) k.w[j] = kk[i].w[j];
        Bytes raw = k.toBytes();
        for (size_t off : findBytes(image.data(), image.size(), raw.data(), raw.size())) {
            KeyHit hit;
            hit.key = k;
            hit.fileOffset = off;
            hit.region = "known";
            hit.method = std::string("stock key present: ") + kk[i].what;
            hit.verified = false;
            res.knownPresent.push_back(hit);
        }
    }

    // ---------------------------------------------------------- index key --
    PackIndex idx;
    bool indexNeedsKey = false;
    if (!eix.empty()) {
        const uint32_t magic = rd32(eix.data());
        if (magic == kMagicEPKD) {
            res.indexEncrypted = false;
            res.indexKeyFound = true;
            res.indexHit.method = "plain EPKD index (no key needed)";
            parseIndexBlob(eix, idx, nullptr);
        } else {
            CryptedObject co;
            if (parseCryptedObjectHeader(eix.data(), eix.size(), co, nullptr)) {
                res.indexEncrypted = co.encrypted();
                indexNeedsKey = co.encrypted();
                if (!indexNeedsKey) {
                    // Compressed but not encrypted: still parse it so the data
                    // key search has entries to work with.
                    res.indexKeyFound = true;
                    res.indexHit.method = "index container is not encrypted";
                    PackKeys none;
                    loadIndexFile(eix, none, idx, nullptr);
                }
            } else {
                res.message += " | .eix is neither EPKD nor MCOZ/MCSP (trying whole-file XTEA)";
                res.indexEncrypted = true;
                indexNeedsKey = true;
            }
        }
    }

    if (indexNeedsKey) {
        size_t done = 0;
        for (const KeyHit& c : candidates) {
            std::string err;
            if (verifyIndexKey(eix, c.key, &idx, &err)) {
                res.indexKeyFound = true;
                res.indexHit = c;
                res.indexHit.verified = true;
                res.candidatesTried = done + 1;
                break;
            }
            if (++done % 200000 == 0 && progress) progress(done, candidates.size(), "index key");
        }
        if (progress) progress(candidates.size(), candidates.size(), "index key");
        if (!res.indexKeyFound) res.message += " | no index key verified";
    }

    // ----------------------------------------------------------- data key --
    if (epk && epkSize > 0 && !idx.entries.empty()) {
        struct Target {
            const uint8_t* blob;
            size_t len;
            uint32_t realSize;
            uint32_t crc;
            std::string name;
        };
        std::vector<Target> targets;
        for (const PackEntry& e : idx.entries) {
            if (targets.size() >= 8) break;
            if (e.dataSize < 32 || e.offset >= epkSize) continue;
            const size_t avail = epkSize - static_cast<size_t>(e.offset);
            const size_t len = std::min<size_t>(e.dataSize, avail);
            const uint8_t* blob = epk + e.offset;
            const uint32_t magic = rd32(blob);
            if (magic != kMagicMCOZ && magic != kMagicMCSP) continue;
            CryptedObject co;
            if (!parseCryptedObjectHeader(blob, len, co, nullptr) || !co.encrypted()) continue;
            if (co.realSize != e.realSize) continue;
            // Prefer mid sized entries: cheap to verify, long enough to be sure.
            if (e.realSize > 8u * 1024u * 1024u) continue;
            targets.push_back({blob, len, e.realSize, e.contentCrc, e.name});
        }
        if (!targets.empty()) {
            res.dataKeyNeeded = true;
            size_t done = 0;
            for (const KeyHit& c : candidates) {
                std::string err;
                if (verifyDataKey(targets[0].blob, targets[0].len, c.key, targets[0].realSize,
                                  targets[0].crc, &err)) {
                    // Confirm against a second entry when one exists.
                    bool confirmed = true;
                    for (size_t t = 1; t < targets.size() && t < 3; ++t) {
                        if (!verifyDataKey(targets[t].blob, targets[t].len, c.key, targets[t].realSize,
                                           targets[t].crc, nullptr)) {
                            confirmed = false;
                            break;
                        }
                    }
                    if (confirmed) {
                        res.dataKeyFound = true;
                        res.dataHit = c;
                        res.dataHit.verified = true;
                        res.candidatesTried = std::max(res.candidatesTried, done + 1);
                        break;
                    }
                }
                if (++done % 200000 == 0 && progress) progress(done, candidates.size(), "data key");
            }
            if (progress) progress(candidates.size(), candidates.size(), "data key");
        }
    }

    // -------------------------------------------------------- heuristics ---
    if ((!res.indexKeyFound && indexNeedsKey) || (res.dataKeyNeeded && !res.dataKeyFound)) {
        std::vector<KeyHit> pool;
        collectAdjacentKeyPairs(image, pe.valid ? &pe : nullptr, pool, 20);
        for (const KeyHit& c : candidates) {
            if (c.method.find("known") != std::string::npos) continue;
            KeyHit h = c;
            h.score = scoreKeyPlausibility(h.key);
            if (h.score >= 14) pool.push_back(h);
            if (pool.size() > 4000) break;
        }
        std::stable_sort(pool.begin(), pool.end(),
                         [](const KeyHit& a, const KeyHit& b) { return a.score > b.score; });
        if (pool.size() > 24) pool.resize(24);
        res.heuristic = std::move(pool);
    }

    return res;
}

}  // namespace m2
