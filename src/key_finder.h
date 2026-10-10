// SPDX-License-Identifier: MIT
// XTEA key recovery from metin2client.exe.
//
// The client keeps two 16 byte keys (four dwords each) in its image:
//   * the index key  -> decrypts every .eix (Crypted Object) header
//   * the data key   -> decrypts type 2 / type 6 entries inside the .epk
// Official builds use the stock keys, private servers usually change them and
// recompile, so the bytes are still sitting in the executable - either as a
// static array in .rdata or as immediates loaded by the code.
//
// Strategy: enumerate candidate dword quadruples, then *verify* them against
// the real .eix (and .epk) instead of guessing. A wrong key never survives the
// verification, so a hit is proof, not a guess.
#pragma once

#include <cstdint>
#include <functional>
#include <string>
#include <vector>

#include "eterpack.h"
#include "pe.h"
#include "util.h"
#include "xtea.h"

namespace m2 {

struct KnownKey {
    const char* what;
    uint32_t w[4];
};
// Documented stock keys (metin2.dev / client source). Private servers that
// never touched EterPack.cpp still use exactly these.
const KnownKey* knownKeys(size_t& count);

struct KeyHit {
    XteaKey key{};
    uint64_t fileOffset = 0;  // where the candidate lives inside the exe
    std::string region;       // section name, "file", or "known"
    std::string method;       // known / rdata-aligned / text-immediates / deep-unaligned
    bool verified = false;    // proved against a real .eix/.epk
    int score = 0;            // heuristic plausibility, only used when unverified
};

struct KeyScanOptions {
    bool includeKnown = true;    // try the documented stock keys first
    bool scanData = true;        // .rdata / .data aligned scan
    bool scanCode = true;        // immediates + aligned scan inside .text
    bool unaligned = false;      // --deep: every byte offset of the image
    size_t maxCandidates = 0;    // 0 = unlimited
};

// Builds the ordered candidate list. Ordered = most likely first, so the
// verification loop usually stops almost immediately.
void collectKeyCandidates(const Bytes& image, const PeImage* pe, const KeyScanOptions& opt,
                          std::vector<KeyHit>& out);

// Plausibility score for heuristic mode (no .eix available to verify against).
int scoreKeyPlausibility(const XteaKey& k);
// Finds 16 byte pairs that sit next to each other, the way the client source
// declares the index key and the data key back to back.
void collectAdjacentKeyPairs(const Bytes& image, const PeImage* pe, std::vector<KeyHit>& out,
                             size_t limit = 40);

// One XTEA block check: does `key` turn the first encrypted dword of a
// Crypted Object into its magic?
bool quickCheckContainer(const uint8_t* data, size_t len, const XteaKey& key, uint32_t expectedMagic);

// Full verification against a .eix image.
bool verifyIndexKey(const Bytes& eix, const XteaKey& key, PackIndex* idx = nullptr,
                    std::string* err = nullptr);
// Full verification against a blob taken out of the .epk.
bool verifyDataKey(const uint8_t* blob, size_t len, const XteaKey& key, uint32_t expectedRealSize,
                   uint32_t expectedCrc, std::string* err = nullptr);

struct KeySearchResult {
    bool indexEncrypted = false;
    bool dataKeyNeeded = false;
    bool indexKeyFound = false;
    bool dataKeyFound = false;
    KeyHit indexHit;
    KeyHit dataHit;
    std::vector<KeyHit> heuristic;  // ranked guesses, only filled when unverified
    std::vector<KeyHit> knownPresent;  // stock keys physically found in the image
    size_t candidatesTried = 0;
    std::string message;
};

using ProgressFn = std::function<void(size_t done, size_t total, const std::string& stage)>;

// Verifies candidates against the .eix (and, when a parsed index + epk image
// are supplied, against a real entry) and reports what was found.
KeySearchResult searchKeys(const Bytes& image, const KeyScanOptions& opt, const Bytes& eix,
                           const uint8_t* epk = nullptr, size_t epkSize = 0,
                           const ProgressFn& progress = nullptr);

}  // namespace m2
