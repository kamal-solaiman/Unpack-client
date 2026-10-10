// SPDX-License-Identifier: MIT
#include "selftest.h"

#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "crc32.h"
#include "crypted_object.h"
#include "eterpack.h"
#include "key_finder.h"
#include "lzo.h"
#include "pe.h"
#include "snappy.h"
#include "testdata.h"
#include "testsupport.h"
#include "util.h"
#include "xtea.h"

namespace m2 {
namespace {

int g_checks = 0;
int g_failures = 0;
bool g_verbose = false;

#define CHECK(cond)                                                       \
    do {                                                                  \
        ++g_checks;                                                       \
        if (!(cond)) {                                                    \
            ++g_failures;                                                 \
            std::printf("  FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond); \
        }                                                                 \
    } while (0)

#define SECTION(name)                                  \
    do {                                               \
        if (g_verbose) std::printf("== %s\n", name);   \
    } while (0)

using m2test::buildPe;
using m2test::buildTestPack;
using m2test::defaultTestFiles;
using m2test::makeKey;
using m2test::randomBytes;
using m2test::sampleText;
using m2test::TestPack;
using m2test::TestSpec;

// ------------------------------------------------------------------ tests --

void testCrcAndXtea() {
    SECTION("crc32 / xtea");
    CHECK(crc32("123456789", 9) == 0xCBF43926u);
    CHECK(crc32Matches(0xCBF43926u, "123456789", 9));
    CHECK(!crc32Matches(0xDEADBEEFu, "123456789", 9));

    const XteaKey key = makeKey(45129401, 92367215, 681285731, 1710201);
    CHECK(key.toByteHex() == "b9 9e b0 02 6f 69 81 05 63 98 9b 28 79 18 1a 00");

    const Bytes plain = sampleText(64, 11);
    const Bytes enc = xteaEncryptPadded(plain.data(), plain.size(), key);
    const Bytes dec = xteaDecryptPadded(enc.data(), enc.size(), key);
    CHECK(dec.size() == plain.size());
    CHECK(dec == plain);

    uint32_t y = 0x11223344, z = 0x55667788;
    const uint32_t y0 = y, z0 = z;
    xteaEncryptBlock(y, z, key);
    CHECK(y != y0 || z != z0);
    xteaDecryptBlock(y, z, key);
    CHECK(y == y0 && z == z0);

    auto parsed = XteaKey::parse("b9 9e b0 02 6f 69 81 05 63 98 9b 28 79 18 1a 00");
    CHECK(parsed.has_value() && *parsed == key);
    auto parsed2 = XteaKey::parse("[45129401, 92367215, 681285731, 1710201]");
    CHECK(parsed2.has_value() && *parsed2 == key);
    auto parsed3 = XteaKey::parse("0x02B09EB9,0x0581696F,0x289B9863,0x001A1879");
    CHECK(parsed3.has_value() && *parsed3 == key);
    CHECK(!XteaKey::parse("zzzz").has_value());
}

void testLzo() {
    SECTION("lzo1x");
    struct Case {
        const char* name;
        const unsigned char* plain;
        size_t plainLen;
        const unsigned char* lzo;
        size_t lzoLen;
    };
    const Case cases[] = {
        {"text", kPlain_text, kPlain_text_len, kLzo_text, kLzo_text_len},
        {"noise", kPlain_noise, kPlain_noise_len, kLzo_noise, kLzo_noise_len},
        {"runs", kPlain_runs, kPlain_runs_len, kLzo_runs, kLzo_runs_len},
        {"binary", kPlain_binary, kPlain_binary_len, kLzo_binary, kLzo_binary_len},
    };
    for (const Case& c : cases) {
        Bytes out;
        std::string err;
        const bool ok = lzo1xDecompressTo(c.lzo, c.lzoLen, c.plainLen, out, &err);
        if (!ok && g_verbose) std::printf("  %s: %s\n", c.name, err.c_str());
        CHECK(ok);
        CHECK(out.size() == c.plainLen);
        CHECK(out.size() == c.plainLen && std::memcmp(out.data(), c.plain, c.plainLen) == 0);

        Bytes out2;
        CHECK(lzo1xDecompressTo(c.lzo, c.lzoLen, 0, out2, &err));
        CHECK(out2 == out);
    }

    // The "stored" encoder must produce streams any LZO1X decoder accepts.
    for (const Case& c : cases) {
        Bytes stored;
        CHECK(lzo1xStore(c.plain, c.plainLen, stored));
        CHECK(stored.size() >= c.plainLen);
        Bytes back;
        std::string err;
        CHECK(lzo1xDecompressTo(stored.data(), stored.size(), c.plainLen, back, &err));
        CHECK(back.size() == c.plainLen);
        CHECK(back.size() == c.plainLen && std::memcmp(back.data(), c.plain, c.plainLen) == 0);
    }

    Bytes tiny;
    CHECK(lzo1xStore(reinterpret_cast<const uint8_t*>("abc"), 3, tiny));
    Bytes tinyBack;
    CHECK(lzo1xDecompressTo(tiny.data(), tiny.size(), 3, tinyBack, nullptr));
    CHECK(tinyBack.size() == 3 && std::memcmp(tinyBack.data(), "abc", 3) == 0);

    const Bytes bigPlain = sampleText(200000, 5);
    Bytes big, bigBack;
    CHECK(lzo1xStore(bigPlain.data(), bigPlain.size(), big));
    CHECK(lzo1xDecompressTo(big.data(), big.size(), bigPlain.size(), bigBack, nullptr));
    CHECK(bigBack == bigPlain);

    const uint8_t junk[] = {0x00, 0xFF, 0x11, 0x22};
    Bytes ignored;
    std::string err;
    CHECK(!lzo1xDecompressTo(junk, sizeof junk, 1000, ignored, &err));
}

void testSnappy() {
    SECTION("snappy");
    struct Case {
        const char* name;
        const unsigned char* plain;
        size_t plainLen;
        const unsigned char* sp;
        size_t spLen;
    };
    const Case cases[] = {
        {"text", kPlain_text, kPlain_text_len, kSnappy_text, kSnappy_text_len},
        {"noise", kPlain_noise, kPlain_noise_len, kSnappy_noise, kSnappy_noise_len},
        {"runs", kPlain_runs, kPlain_runs_len, kSnappy_runs, kSnappy_runs_len},
        {"binary", kPlain_binary, kPlain_binary_len, kSnappy_binary, kSnappy_binary_len},
    };
    for (const Case& c : cases) {
        Bytes out;
        std::string err;
        CHECK(snappyDecompressTo(c.sp, c.spLen, c.plainLen, out, &err));
        CHECK(out.size() == c.plainLen);
        CHECK(out.size() == c.plainLen && std::memcmp(out.data(), c.plain, c.plainLen) == 0);

        Bytes stored;
        CHECK(snappyStore(c.plain, c.plainLen, stored));
        Bytes back;
        CHECK(snappyDecompressTo(stored.data(), stored.size(), c.plainLen, back, &err));
        CHECK(back == out);
    }
    size_t declared = 0;
    CHECK(snappyUncompressedLength(kSnappy_runs, kSnappy_runs_len, declared));
    CHECK(declared == kPlain_runs_len);
}

void testCryptedObject() {
    SECTION("crypted object");
    const XteaKey key = makeKey(0x0A1B2C3D, 0x4E5F6071, 0x8293A4B5, 0xC6D7E8F9);
    const XteaKey wrong = makeKey(1, 2, 3, 4);
    const Bytes plain = sampleText(4096, 3);

    for (uint32_t magic : {kMagicMCOZ, kMagicMCSP}) {
        Bytes packed, decoded;
        std::string err;
        CHECK(cryptedObjectEncode(plain, &key, magic, packed, &err));
        CHECK(packed.size() > 16);
        CHECK(rd32(packed.data()) == magic);

        CryptedObject co;
        CHECK(parseCryptedObjectHeader(packed.data(), packed.size(), co, &err));
        CHECK(co.encrypted());
        CHECK(co.realSize == plain.size());
        CHECK(!cryptedObjectKeyLooksRight(packed.data(), packed.size(), wrong, co));
        CHECK(cryptedObjectKeyLooksRight(packed.data(), packed.size(), key, co));

        CHECK(!cryptedObjectDecode(packed.data(), packed.size(), &wrong, decoded, &err));
        CHECK(cryptedObjectDecode(packed.data(), packed.size(), &key, decoded, &err));
        CHECK(decoded == plain);

        Bytes packedPlain;
        CHECK(cryptedObjectEncode(plain, nullptr, magic, packedPlain, &err));
        CHECK(parseCryptedObjectHeader(packedPlain.data(), packedPlain.size(), co, &err));
        CHECK(!co.encrypted());
        CHECK(rd32(packedPlain.data() + 16) == magic);
        CHECK(cryptedObjectDecode(packedPlain.data(), packedPlain.size(), nullptr, decoded, &err));
        CHECK(decoded == plain);
        CHECK(cryptedObjectDecode(packedPlain.data(), packedPlain.size(), &key, decoded, &err));
        CHECK(decoded == plain);
    }

    const Bytes garbage = randomBytes(64, 9);
    CryptedObject co;
    std::string err;
    CHECK(!parseCryptedObjectHeader(garbage.data(), garbage.size(), co, &err));
}

void testPackRoundTrip(const EntryLayout& layout, bool encryptIndex, uint32_t indexMagic,
                       const char* label) {
    SECTION(label);
    TestSpec spec;
    spec.indexKey = makeKey(0x11223344, 0x55667788, 0x99AABBCC, 0xDDEEFF01);
    spec.dataKey = makeKey(0x0A1B2C3D, 0x4E5F6071, 0x8293A4B5, 0xC6D7E8F9);
    spec.layout = &layout;
    spec.encryptIndex = encryptIndex;
    spec.indexMagic = indexMagic;
    spec.files = defaultTestFiles();

    TestPack pack;
    std::string err;
    CHECK(buildTestPack(spec, pack, &err));

    PackKeys keys;
    keys.indexKey = spec.indexKey;
    keys.haveIndexKey = encryptIndex;
    keys.dataKey = spec.dataKey;
    keys.haveDataKey = true;

    PackIndex idx;
    const bool loaded = loadIndexFile(pack.eix, keys, idx, &err);
    if (!loaded && g_verbose) std::printf("  %s\n", err.c_str());
    CHECK(loaded);
    if (!loaded) return;
    CHECK(idx.version == 2);
    CHECK(idx.entries.size() == pack.files.size());
    CHECK(idx.layout == &layout);

    for (size_t i = 0; i < idx.entries.size(); ++i) {
        const PackEntry& e = idx.entries[i];
        CHECK(e.name == pack.files[i].name);
        CHECK(e.realSize == pack.files[i].content.size());
        CHECK(e.type == pack.files[i].type);

        Bytes out;
        ExtractInfo info;
        const bool ok = extractEntry(pack.epk.data(), pack.epk.size(), e, keys, false, out, info, &err);
        if (!ok && g_verbose) std::printf("  %s: %s\n", e.name.c_str(), err.c_str());
        CHECK(ok);
        CHECK(out == pack.files[i].content);
        if (!out.empty()) CHECK(info.crcOk);
        CHECK(e.safePath == sanitizeVirtualPath(e.name));
    }

    // Auto detection must cope with a lying index (every type forced to 2).
    PackIndex lied = idx;
    for (PackEntry& e : lied.entries) e.type = PACK_TYPE_LZO_XTEA;
    size_t autoOk = 0;
    for (const PackEntry& e : lied.entries) {
        Bytes out;
        ExtractInfo info;
        if (extractEntry(pack.epk.data(), pack.epk.size(), e, keys, true, out, info, nullptr)) {
            ++autoOk;
            CHECK(out.size() == e.realSize);
        }
    }
    CHECK(autoOk == lied.entries.size());

    // Auto detection without the data key must still rescue the plain entries.
    PackKeys onlyIndex;
    onlyIndex.indexKey = spec.indexKey;
    onlyIndex.haveIndexKey = encryptIndex;
    size_t rescued = 0;
    for (const PackEntry& e : idx.entries) {
        Bytes out;
        ExtractInfo info;
        if (extractEntry(pack.epk.data(), pack.epk.size(), e, onlyIndex, true, out, info, nullptr))
            ++rescued;
    }
    CHECK(rescued >= 3);  // raw + lzo + empty

    if (encryptIndex && indexMagic != 0) {
        PackKeys bad;
        bad.indexKey = makeKey(9, 9, 9, 9);
        bad.haveIndexKey = true;
        PackIndex dummy;
        CHECK(!loadIndexFile(pack.eix, bad, dummy, &err));
    }
}

void testPathSanitizer() {
    SECTION("path sanitizer");
    CHECK(sanitizeVirtualPath("d:/ymir art/effect/a.dds") == "ymir art/effect/a.dds");
    CHECK(sanitizeVirtualPath("locale\\europe\\locale.txt") == "locale/europe/locale.txt");
    CHECK(sanitizeVirtualPath("../../etc/passwd").empty());
    CHECK(sanitizeVirtualPath("a/./b//c") == "a/b/c");
    CHECK(sanitizeVirtualPath("bad:name?.txt") == "bad_name_.txt");
    CHECK(sanitizeVirtualPath("").empty());
}

void testPeParser() {
    SECTION("pe parser");
    const Bytes image = buildPe({{".text", randomBytes(3000, 21)}, {".rdata", randomBytes(600, 22)}});
    PeImage pe;
    std::string err;
    CHECK(looksLikePe(image.data(), image.size()));
    CHECK(parsePe(image.data(), image.size(), pe, &err));
    CHECK(pe.valid);
    CHECK(pe.sections.size() == 2);
    CHECK(pe.sections[0].name == ".text");
    CHECK(pe.sections[0].executable());
    CHECK(pe.sections[1].name == ".rdata");
    CHECK(!pe.sections[1].executable());
    CHECK(!pe.pe32plus);
    CHECK(pe.imageBase == 0x00400000);

    const uint8_t notPe[] = {'M', 'Z', 0, 0};
    CHECK(!looksLikePe(notPe, sizeof notPe));
}

void testKeyFinderRdata() {
    SECTION("key finder (.rdata array)");
    TestSpec spec;
    spec.indexKey = makeKey(0x11223344, 0x55667788, 0x99AABBCC, 0xDDEEFF01);
    spec.dataKey = makeKey(0x0A1B2C3D, 0x4E5F6071, 0x8293A4B5, 0xC6D7E8F9);
    spec.files = defaultTestFiles(31);
    TestPack pack;
    std::string err;
    CHECK(buildTestPack(spec, pack, &err));

    Bytes rdata = randomBytes(1024, 32);
    while (rdata.size() % 4) rdata.push_back(0);
    const size_t keyOff = rdata.size();
    const Bytes ib = spec.indexKey.toBytes();
    const Bytes db = spec.dataKey.toBytes();
    rdata.insert(rdata.end(), ib.begin(), ib.end());
    rdata.insert(rdata.end(), db.begin(), db.end());
    const std::string strTable("some string table\0padding", 25);
    rdata.insert(rdata.end(), strTable.begin(), strTable.end());

    const Bytes image = buildPe({{".text", randomBytes(8192, 33)}, {".rdata", rdata}});
    PeImage pe;
    CHECK(parsePe(image.data(), image.size(), pe, nullptr));
    const uint64_t rdataFilePtr = pe.sections[1].rawPtr;

    KeyScanOptions opt;
    KeySearchResult res = searchKeys(image, opt, pack.eix, pack.epk.data(), pack.epk.size(), nullptr);
    CHECK(res.indexEncrypted);
    CHECK(res.indexKeyFound);
    CHECK(res.indexHit.key == spec.indexKey);
    CHECK(res.indexHit.verified);
    CHECK(res.indexHit.fileOffset == rdataFilePtr + keyOff);
    CHECK(res.dataKeyNeeded);
    CHECK(res.dataKeyFound);
    CHECK(res.dataHit.key == spec.dataKey);
    CHECK(res.dataHit.fileOffset == rdataFilePtr + keyOff + 16);
    CHECK(res.heuristic.empty());
}

void testKeyFinderImmediates() {
    SECTION("key finder (code immediates)");
    TestSpec spec;
    spec.indexKey = makeKey(0x77AA11BB, 0x22CC33DD, 0x44EE55FF, 0x66007788);
    spec.dataKey = makeKey(0x10203040, 0x50607080, 0x90A0B0C0, 0xD0E0F011);
    spec.files = defaultTestFiles(41);
    TestPack pack;
    std::string err;
    CHECK(buildTestPack(spec, pack, &err));

    Bytes text = randomBytes(512, 42);
    m2test::appendPushImmediates(text, spec.indexKey);
    const Bytes gap = randomBytes(128, 43);
    text.insert(text.end(), gap.begin(), gap.end());
    m2test::appendPushImmediates(text, spec.dataKey);
    const Bytes tail = randomBytes(256, 44);
    text.insert(text.end(), tail.begin(), tail.end());

    const Bytes image = buildPe({{".text", text}, {".rdata", randomBytes(4096, 45)}});
    KeyScanOptions opt;
    KeySearchResult res = searchKeys(image, opt, pack.eix, pack.epk.data(), pack.epk.size(), nullptr);
    CHECK(res.indexKeyFound);
    CHECK(res.indexHit.key == spec.indexKey);
    CHECK(res.indexHit.method.find("immediates") != std::string::npos);
    CHECK(res.dataKeyFound);
    CHECK(res.dataHit.key == spec.dataKey);
}

void testKeyFinderStockKeys() {
    SECTION("key finder (stock keys)");
    size_t n = 0;
    const KnownKey* kk = knownKeys(n);
    TestSpec spec;
    for (int i = 0; i < 4; ++i) {
        spec.indexKey.w[i] = kk[0].w[i];
        spec.dataKey.w[i] = kk[1].w[i];
    }
    spec.files = defaultTestFiles(51);
    TestPack pack;
    std::string err;
    CHECK(buildTestPack(spec, pack, &err));

    Bytes rdata = randomBytes(2048, 52);
    const Bytes ib = spec.indexKey.toBytes();
    rdata.insert(rdata.end(), ib.begin(), ib.end());
    const Bytes image = buildPe({{".text", randomBytes(4096, 53)}, {".rdata", rdata}});

    KeyScanOptions opt;
    KeySearchResult res = searchKeys(image, opt, pack.eix, pack.epk.data(), pack.epk.size(), nullptr);
    CHECK(res.indexKeyFound);
    CHECK(res.indexHit.key == spec.indexKey);
    CHECK(res.dataKeyFound);
    CHECK(res.dataHit.key == spec.dataKey);
    bool sawStock = false;
    for (const KeyHit& h : res.knownPresent)
        if (h.key == spec.indexKey) sawStock = true;
    CHECK(sawStock);
}

void testKeyFinderFailure() {
    SECTION("key finder (no key present)");
    TestSpec spec;
    spec.indexKey = makeKey(0xDEADC0DE, 0xBADF00D1, 0x12345678, 0x9ABCDEF0);
    spec.dataKey = makeKey(0x0F0F0F0F, 0x12121212, 0x34343434, 0x56565656);
    spec.files = defaultTestFiles(61);
    TestPack pack;
    std::string err;
    CHECK(buildTestPack(spec, pack, &err));

    const Bytes image = buildPe({{".text", randomBytes(8192, 62)}, {".rdata", randomBytes(8192, 63)}});
    KeyScanOptions opt;
    KeySearchResult res = searchKeys(image, opt, pack.eix, pack.epk.data(), pack.epk.size(), nullptr);
    CHECK(!res.indexKeyFound);
    CHECK(!res.dataKeyFound);
    CHECK(!res.heuristic.empty());  // still offers ranked guesses

    // A deep scan of an image without the key must not crash and must stay wrong.
    KeyScanOptions deep;
    deep.unaligned = true;
    KeySearchResult res2 = searchKeys(image, deep, pack.eix, pack.epk.data(), pack.epk.size(), nullptr);
    CHECK(!res2.indexKeyFound);
    CHECK(!res2.dataKeyFound);
}

void testIndexLayouts() {
    SECTION("index layout detection");
    size_t count = 0;
    const EntryLayout* layouts = entryLayouts(count);
    CHECK(count >= 2);
    for (size_t i = 0; i < count; ++i) {
        TestSpec spec;
        spec.indexKey = makeKey(0x51525354, 0x55565758, 0x595A5B5C, 0x5D5E5F60);
        spec.dataKey = makeKey(0x61626364, 0x65666768, 0x696A6B6C, 0x6D6E6F70);
        spec.layout = &layouts[i];
        spec.files = defaultTestFiles(static_cast<uint32_t>(70 + i));
        TestPack pack;
        std::string err;
        CHECK(buildTestPack(spec, pack, &err));

        PackKeys keys;
        keys.indexKey = spec.indexKey;
        keys.haveIndexKey = true;
        keys.dataKey = spec.dataKey;
        keys.haveDataKey = true;

        PackIndex idx;
        if (!loadIndexFile(pack.eix, keys, idx, &err)) {
            if (g_verbose) std::printf("  layout %s: %s\n", layouts[i].name, err.c_str());
            CHECK(false);
            continue;
        }
        CHECK(idx.layout == &layouts[i]);
        CHECK(idx.entries.size() == pack.files.size());
        for (size_t f = 0; f < idx.entries.size(); ++f) {
            Bytes out;
            ExtractInfo info;
            CHECK(extractEntry(pack.epk.data(), pack.epk.size(), idx.entries[f], keys, false, out, info,
                               &err));
            CHECK(out == pack.files[f].content);
        }
    }
}

void testPlainIndex() {
    SECTION("plain EPKD index");
    TestSpec spec;
    spec.dataKey = makeKey(0x21222324, 0x25262728, 0x292A2B2C, 0x2D2E2F30);
    spec.encryptIndex = false;
    spec.indexMagic = 0;  // no container at all
    spec.files = defaultTestFiles(81);
    TestPack pack;
    std::string err;
    CHECK(buildTestPack(spec, pack, &err));
    CHECK(rd32(pack.eix.data()) == kMagicEPKD);

    PackKeys keys;
    keys.dataKey = spec.dataKey;
    keys.haveDataKey = true;
    PackIndex idx;
    CHECK(loadIndexFile(pack.eix, keys, idx, &err));
    CHECK(!idx.indexWasEncrypted);
    CHECK(idx.entries.size() == pack.files.size());
    for (size_t f = 0; f < idx.entries.size(); ++f) {
        Bytes out;
        ExtractInfo info;
        CHECK(extractEntry(pack.epk.data(), pack.epk.size(), idx.entries[f], keys, true, out, info, &err));
        CHECK(out == pack.files[f].content);
    }
}

void testWholeFileCipher() {
    SECTION("whole-file XTEA index");
    TestSpec spec;
    spec.indexKey = makeKey(0xAABBCCDD, 0x11223344, 0x55667788, 0x99AABBCC);
    spec.dataKey = makeKey(0x01020304, 0x05060708, 0x090A0B0C, 0x0D0E0F10);
    spec.indexMagic = 0;  // build a plain EPKD index first
    spec.encryptIndex = false;
    spec.files = defaultTestFiles(101);
    TestPack pack;
    std::string err;
    CHECK(buildTestPack(spec, pack, &err));

    // A server that XTEAs the entire .eix, header included.
    Bytes whole = xteaEncryptPadded(pack.eix.data(), pack.eix.size(), spec.indexKey);
    CHECK(rd32(whole.data()) != kMagicEPKD);

    PackKeys keys;
    keys.indexKey = spec.indexKey;
    keys.haveIndexKey = true;
    keys.dataKey = spec.dataKey;
    keys.haveDataKey = true;
    keys.fallbacks.push_back(spec.indexKey);

    PackIndex idx;
    CHECK(loadIndexFile(whole, keys, idx, &err));
    if (g_verbose && !err.empty()) std::printf("  %s\n", err.c_str());
    CHECK(idx.fullFileCipher);
    CHECK(idx.entries.size() == pack.files.size());
    if (idx.entries.size() == pack.files.size()) {
        for (size_t f = 0; f < idx.entries.size(); ++f) {
            Bytes out;
            ExtractInfo info;
            CHECK(extractEntry(pack.epk.data(), pack.epk.size(), idx.entries[f], keys, true, out, info,
                               &err));
            CHECK(out == pack.files[f].content);
        }
    }

    // The key finder must recover the key for this variant too.
    Bytes rdata = randomBytes(512, 102);
    const Bytes ib = spec.indexKey.toBytes();
    const Bytes db = spec.dataKey.toBytes();
    rdata.insert(rdata.end(), ib.begin(), ib.end());
    rdata.insert(rdata.end(), db.begin(), db.end());
    const Bytes image = buildPe({{".text", randomBytes(1024, 103)}, {".rdata", rdata}});
    KeyScanOptions opt;
    KeySearchResult res = searchKeys(image, opt, whole, pack.epk.data(), pack.epk.size(), nullptr);
    CHECK(res.indexKeyFound);
    CHECK(res.indexHit.key == spec.indexKey);
}

void testCrcMismatchTolerance() {
    SECTION("CRC mismatch tolerance");
    TestSpec spec;
    spec.indexKey = makeKey(0x1F2E3D4C, 0x5B6A7988, 0x97A6B5C4, 0xD3E2F100);
    spec.dataKey = makeKey(0x0E1F2E3D, 0x4C5B6A79, 0x8897A6B5, 0xC4D3E2F1);
    spec.indexMagic = 0;
    spec.encryptIndex = false;
    spec.files = defaultTestFiles(111);
    TestPack pack;
    std::string err;
    CHECK(buildTestPack(spec, pack, &err));

    PackKeys keys;
    keys.dataKey = spec.dataKey;
    keys.haveDataKey = true;
    PackIndex idx;
    CHECK(loadIndexFile(pack.eix, keys, idx, &err));
    CHECK(idx.entries.size() >= 3);
    if (idx.entries.size() < 3) return;

    // Corrupt the stored CRC of one entry: the data is still perfectly good.
    idx.entries[2].contentCrc ^= 0xDEADBEEFu;
    Bytes out;
    ExtractInfo info;
    CHECK(extractEntry(pack.epk.data(), pack.epk.size(), idx.entries[2], keys, true, out, info, &err));
    CHECK(out == pack.files[2].content);
    CHECK(info.crcChecked && !info.crcOk);
    CHECK(info.method.find("CRC mismatch") != std::string::npos);
    CHECK(extractEntry(pack.epk.data(), pack.epk.size(), idx.entries[2], keys, false, out, info, &err));
    CHECK(out == pack.files[2].content);

    // An intact entry must still report a clean CRC.
    CHECK(extractEntry(pack.epk.data(), pack.epk.size(), idx.entries[1], keys, true, out, info, &err));
    CHECK(!info.crcChecked || info.crcOk);
}

void testUnknownTypes() {
    SECTION("unsupported types");
    TestSpec spec;
    spec.dataKey = makeKey(0x31323334, 0x35363738, 0x393A3B3C, 0x3D3E3F40);
    spec.files = {{"panama.bin", sampleText(300, 91), PACK_TYPE_PANAMA},
                  {"hybrid.bin", sampleText(300, 92), PACK_TYPE_HYBRID}};
    spec.indexMagic = 0;
    spec.encryptIndex = false;
    TestPack pack;
    std::string err;
    CHECK(buildTestPack(spec, pack, &err));

    PackKeys keys;
    keys.dataKey = spec.dataKey;
    keys.haveDataKey = true;
    PackIndex idx;
    CHECK(loadIndexFile(pack.eix, keys, idx, &err));
    CHECK(idx.entries.size() == 2);
    if (idx.entries.size() != 2) return;
    CHECK(!packTypeSupported(PACK_TYPE_PANAMA));
    CHECK(!packTypeSupported(PACK_TYPE_HYBRID));

    Bytes out;
    ExtractInfo info;
    // The blobs are raw in this synthetic pack, so auto detection recovers them
    // anyway; strict mode must refuse.
    CHECK(!extractEntry(pack.epk.data(), pack.epk.size(), idx.entries[0], keys, false, out, info, &err));
    CHECK(err.find("unsupported") != std::string::npos);
    CHECK(extractEntry(pack.epk.data(), pack.epk.size(), idx.entries[0], keys, true, out, info, &err));
    CHECK(out == pack.files[0].content);
}

}  // namespace

int runSelfTests(bool verbose) {
    g_verbose = verbose;
    g_checks = 0;
    g_failures = 0;

    std::printf("running self tests...\n");
    testCrcAndXtea();
    testLzo();
    testSnappy();
    testCryptedObject();
    testPathSanitizer();
    testPeParser();
    testPackRoundTrip(classicLayout(), true, kMagicMCOZ, "pack round trip (MCOZ index, classic layout)");
    testPackRoundTrip(classicLayout(), true, kMagicMCSP, "pack round trip (MCSP index)");
    testPackRoundTrip(classicLayout(), false, kMagicMCOZ, "pack round trip (compressed, unencrypted index)");
    testIndexLayouts();
    testPlainIndex();
    testWholeFileCipher();
    testCrcMismatchTolerance();
    testUnknownTypes();
    testKeyFinderRdata();
    testKeyFinderImmediates();
    testKeyFinderStockKeys();
    testKeyFinderFailure();

    std::printf("%d checks, %d failures\n", g_checks, g_failures);
    if (g_failures == 0) std::printf("ALL TESTS PASSED\n");
    return g_failures == 0 ? 0 : 1;
}

}  // namespace m2
