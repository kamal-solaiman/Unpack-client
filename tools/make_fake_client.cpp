// SPDX-License-Identifier: MIT
// Builds a synthetic Metin2 client on disk so the unpacker can be tested end
// to end without a real (and copyrighted) client:
//
//   <out>/metin2client.exe   PE image holding the two XTEA keys
//   <out>/data/root.eix      encrypted index (MCOZ + XTEA)
//   <out>/data/root.epk      content file (types 0, 1, 2 and 6)
//   <out>/_expected/...      the same files in plain form, for `diff -r`
//   <out>/keys.txt           the keys that were used
#include <cstdio>
#include <string>
#include <vector>

#include "eterpack.h"
#include "testsupport.h"
#include "unpacker.h"
#include "util.h"

namespace {

std::vector<m2test::TestFile> realisticFiles(size_t count, uint32_t seed) {
    static const char* const names[] = {
        "locale/europe/locale.txt",
        "locale/europe/logininfo.py",
        "locale/game/40k/itemdesc.txt",
        "userinterface/loginwindow.py",
        "userinterface/game.py",
        "userinterface/intrologin.py",
        "d:/ymir art/effect/etc/game/2013_back02.dds",
        "d:/ymir art/gui/game/option.tga",
        "d:/ymir art/font/english_game_15.fnt",
        "sound/engine/snd_eng_game.mp3",
        "season1/effect/etc/bag.dds",
        "attribute/42_12.atr",
        "guild/flag/flag_data.txt",
        "maps/emperors/empire_a/setting.cfg",
    };
    std::vector<m2test::TestFile> files;
    for (size_t i = 0; i < count; ++i) {
        m2test::TestFile f;
        char suffix[32];
        std::snprintf(suffix, sizeof suffix, "%03zu_", i);
        f.name = std::string(suffix) + names[i % (sizeof(names) / sizeof(names[0]))];
        const size_t size = static_cast<size_t>(60 + ((seed * 31 + i * 977) % 40000));
        f.content = m2test::sampleText(size, seed + static_cast<uint32_t>(i) * 13u);
        switch (i % 4) {
            case 0: f.type = m2::PACK_TYPE_RAW; break;
            case 1: f.type = m2::PACK_TYPE_LZO; break;
            case 2: f.type = m2::PACK_TYPE_LZO_XTEA; break;
            default: f.type = m2::PACK_TYPE_SNAPPY_XTEA; break;
        }
        files.push_back(std::move(f));
    }
    return files;
}

}  // namespace

int main(int argc, char** argv) {
    std::string outDir = argc > 1 ? argv[1] : "fake_client";
    size_t fileCount = 24;
    uint32_t seed = 20240910;
    std::string layoutName = "classic";
    std::string indexMagic = "MCOZ";
    bool encryptIndex = true;
    bool keysInCode = false;
    size_t textKb = 20;
    size_t rdataKb = 30;

    for (int i = 2; i < argc; ++i) {
        const std::string a = argv[i];
        if (a == "--files" && i + 1 < argc) fileCount = static_cast<size_t>(std::stoul(argv[++i]));
        else if (a == "--seed" && i + 1 < argc) seed = static_cast<uint32_t>(std::stoul(argv[++i]));
        else if (a == "--layout" && i + 1 < argc) layoutName = argv[++i];
        else if (a == "--index-magic" && i + 1 < argc) indexMagic = argv[++i];
        else if (a == "--no-encrypt-index") encryptIndex = false;
        else if (a == "--keys-in-code") keysInCode = true;
        else if (a == "--text-kb" && i + 1 < argc) textKb = static_cast<size_t>(std::stoul(argv[++i]));
        else if (a == "--rdata-kb" && i + 1 < argc) rdataKb = static_cast<size_t>(std::stoul(argv[++i]));
        else {
            std::fprintf(stderr, "unknown argument: %s\n", a.c_str());
            return 2;
        }
    }

    size_t layoutCount = 0;
    const m2::EntryLayout* layouts = m2::entryLayouts(layoutCount);
    const m2::EntryLayout* layout = nullptr;
    for (size_t i = 0; i < layoutCount; ++i) {
        const std::string n = layouts[i].name;
        if (n.rfind(layoutName, 0) == 0) layout = &layouts[i];
    }
    if (!layout) {
        std::fprintf(stderr, "unknown layout '%s'\n", layoutName.c_str());
        return 2;
    }

    m2test::TestSpec spec;
    spec.indexKey = m2test::makeKey(0x1A2B3C4D + seed, 0x5E6F7080 ^ seed, 0x91A2B3C4 + seed / 7,
                                    0xD5E6F708 - seed % 1000);
    spec.dataKey = m2test::makeKey(0x0F1E2D3C + seed, 0x4B5A6978 ^ seed, 0x8796A5B4 + seed / 3,
                                   0xC3D2E1F0 - seed % 777);
    spec.layout = layout;
    spec.encryptIndex = encryptIndex;
    spec.indexMagic = indexMagic == "plain" ? 0u : (indexMagic == "MCSP" ? m2::kMagicMCSP : m2::kMagicMCOZ);
    spec.files = realisticFiles(fileCount, seed);

    m2test::TestPack pack;
    std::string err;
    if (!m2test::buildTestPack(spec, pack, &err)) {
        std::fprintf(stderr, "cannot build the pack: %s\n", err.c_str());
        return 1;
    }

    // ---- the fake executable ------------------------------------------------
    m2::Bytes text = m2test::randomBytes(textKb * 1024, seed + 1);
    m2::Bytes rdata = m2test::randomBytes(rdataKb * 1024, seed + 2);
    const std::string marker = "EterPack keys (synthetic test image)";
    rdata.insert(rdata.end(), marker.begin(), marker.end());
    if (keysInCode) {
        m2test::appendPushImmediates(text, spec.indexKey);
        const m2::Bytes gap = m2test::randomBytes(64, seed + 3);
        text.insert(text.end(), gap.begin(), gap.end());
        m2test::appendPushImmediates(text, spec.dataKey);
    } else {
        while (rdata.size() % 4) rdata.push_back(0);
        const m2::Bytes ib = spec.indexKey.toBytes();
        const m2::Bytes db = spec.dataKey.toBytes();
        rdata.insert(rdata.end(), ib.begin(), ib.end());
        rdata.insert(rdata.end(), db.begin(), db.end());
    }
    const m2::Bytes image = m2test::buildPe({{".text", text}, {".rdata", rdata}, {".data", m2::Bytes(2048, 0)}});

    // ---- write everything --------------------------------------------------
    const std::string dataDir = m2::joinPath(outDir, "data");
    if (!m2::writeFile(m2::joinPath(outDir, "metin2client.exe"), image)) {
        std::fprintf(stderr, "cannot write the fake exe\n");
        return 1;
    }
    if (!m2::writeFile(m2::joinPath(dataDir, "root.eix"), pack.eix)) {
        std::fprintf(stderr, "cannot write root.eix\n");
        return 1;
    }
    if (!m2::writeFile(m2::joinPath(dataDir, "root.epk"), pack.epk)) {
        std::fprintf(stderr, "cannot write root.epk\n");
        return 1;
    }
    const std::string expected = m2::joinPath(outDir, "_expected");
    for (const m2test::TestFile& f : pack.files) {
        const std::string rel = m2::sanitizeVirtualPath(f.name);
        if (!m2::writeFile(m2::joinPath(expected, rel), f.content)) {
            std::fprintf(stderr, "cannot write expected file %s\n", rel.c_str());
            return 1;
        }
    }
    std::string keysTxt;
    keysTxt += "# synthetic client keys generated by tools/make_fake_client\n";
    keysTxt += "index_key_bytes = " + spec.indexKey.toByteHex() + "\n";
    keysTxt += "index_key_dwords = " + spec.indexKey.toDwordArray() + "\n";
    keysTxt += "data_key_bytes = " + spec.dataKey.toByteHex() + "\n";
    keysTxt += "data_key_dwords = " + spec.dataKey.toDwordArray() + "\n";
    keysTxt += "index_encrypted = " + std::string(encryptIndex ? "yes" : "no") + "\n";
    keysTxt += "index_container = " + indexMagic + "\n";
    keysTxt += "layout = " + std::string(layout->name) + "\n";
    keysTxt += "keys_hidden_in = " + std::string(keysInCode ? "code immediates" : ".rdata array") + "\n";
    keysTxt += "files = " + std::to_string(pack.files.size()) + "\n";
    if (!m2::writeFile(m2::joinPath(outDir, "keys.txt"), keysTxt)) return 1;

    std::printf("fake client written to %s\n", outDir.c_str());
    std::printf("  metin2client.exe : %s (%s)\n", m2::humanSize(image.size()).c_str(),
                keysInCode ? "keys hidden as code immediates" : "keys as a .rdata array");
    std::printf("  data/root.eix    : %s, container %s, encrypted %s\n",
                m2::humanSize(pack.eix.size()).c_str(), indexMagic.c_str(),
                encryptIndex ? "yes" : "no");
    std::printf("  data/root.epk    : %s, %zu entries, layout %s\n",
                m2::humanSize(pack.epk.size()).c_str(), pack.files.size(), layout->name);
    std::printf("  index key        : %s\n", spec.indexKey.toByteHex().c_str());
    std::printf("  data  key        : %s\n", spec.dataKey.toByteHex().c_str());
    std::printf("  plain copies     : %s\n", expected.c_str());
    return 0;
}
