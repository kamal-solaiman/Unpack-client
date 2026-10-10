// SPDX-License-Identifier: MIT
#include "testsupport.h"

#include <cstring>

#include "crc32.h"

namespace m2test {

Bytes randomBytes(size_t n, uint32_t seed) {
    Bytes out(n);
    uint32_t s = seed ? seed : 1u;
    for (size_t i = 0; i < n; ++i) {
        s = s * 1664525u + 1013904223u;
        out[i] = static_cast<uint8_t>(s >> 16);
    }
    return out;
}

XteaKey makeKey(uint32_t a, uint32_t b, uint32_t c, uint32_t d) {
    XteaKey k;
    k.w[0] = a;
    k.w[1] = b;
    k.w[2] = c;
    k.w[3] = d;
    return k;
}

Bytes sampleText(size_t n, uint32_t seed) {
    static const char* base = "Metin2 EterPack payload - unpack data/root. locale/europe ";
    Bytes out;
    const size_t len = std::strlen(base);
    while (out.size() < n) out.insert(out.end(), base, base + len);
    out.resize(n);
    uint32_t s = seed ? seed : 1u;
    for (size_t i = 0; i < n; i += 61) {
        s = s * 1664525u + 1013904223u;
        out[i] = static_cast<uint8_t>(s >> 16);
    }
    return out;
}

Bytes buildPe(const std::vector<std::pair<std::string, Bytes>>& sections) {
    const size_t headerSize = 0x400;
    const size_t lfanew = 0x80;
    const size_t sizeOfOptional = 224;

    size_t total = headerSize;
    for (const auto& sec : sections) total += (sec.second.size() + 0x1FF) & ~static_cast<size_t>(0x1FF);
    Bytes img(total, 0);

    img[0] = 'M';
    img[1] = 'Z';
    m2::wr32(img.data() + 0x3C, static_cast<uint32_t>(lfanew));
    img[lfanew] = 'P';
    img[lfanew + 1] = 'E';

    uint8_t* coff = img.data() + lfanew + 4;
    m2::wr16(coff, 0x014C);  // i386
    m2::wr16(coff + 2, static_cast<uint16_t>(sections.size()));
    m2::wr16(coff + 16, static_cast<uint16_t>(sizeOfOptional));
    m2::wr16(coff + 18, 0x0102);

    uint8_t* opt = coff + 20;
    m2::wr16(opt, 0x10B);                                   // PE32
    m2::wr32(opt + 16, 0x1000);                             // entry point
    m2::wr32(opt + 28, 0x00400000);                         // image base
    m2::wr32(opt + 32, 0x1000);                             // section alignment
    m2::wr32(opt + 36, 0x200);                              // file alignment
    m2::wr32(opt + 56, 0x100000);                           // size of image
    m2::wr32(opt + 60, static_cast<uint32_t>(headerSize));  // size of headers

    uint32_t rawPtr = static_cast<uint32_t>(headerSize);
    uint32_t vaddr = 0x1000;
    for (size_t i = 0; i < sections.size(); ++i) {
        uint8_t* sh = opt + sizeOfOptional + i * 40;
        std::memset(sh, 0, 40);
        std::memcpy(sh, sections[i].first.c_str(),
                    sections[i].first.size() < 8 ? sections[i].first.size() : 8);
        m2::wr32(sh + 8, static_cast<uint32_t>(sections[i].second.size()));   // virtual size
        m2::wr32(sh + 12, vaddr);
        m2::wr32(sh + 16, static_cast<uint32_t>(sections[i].second.size()));  // raw size
        m2::wr32(sh + 20, rawPtr);
        const bool isText = sections[i].first == ".text";
        m2::wr32(sh + 36, isText ? 0x60000020u : 0x40000040u);

        std::memcpy(img.data() + rawPtr, sections[i].second.data(), sections[i].second.size());
        rawPtr = (rawPtr + static_cast<uint32_t>(sections[i].second.size()) + 0x1FFu) & ~0x1FFu;
        vaddr += 0x1000;
    }
    return img;
}

void appendPushImmediates(Bytes& code, const XteaKey& key) {
    for (int i = 0; i < 4; ++i) {
        code.push_back(0x68);  // push imm32
        uint8_t tmp[4];
        m2::wr32(tmp, key.w[i]);
        code.insert(code.end(), tmp, tmp + 4);
    }
    code.push_back(0xC3);  // ret
}

std::vector<TestFile> defaultTestFiles(uint32_t seed) {
    std::vector<TestFile> files;
    files.push_back({"locale/europe/locale.txt", sampleText(600, seed), m2::PACK_TYPE_RAW});
    files.push_back({"userinterface/loginwindow.py", sampleText(1500, seed + 1), m2::PACK_TYPE_LZO});
    files.push_back({"d:/ymir art/effect/etc/game/back02.dds", sampleText(3000, seed + 2),
                     m2::PACK_TYPE_LZO_XTEA});
    files.push_back({"sound/engine/snd_eng_game.mp3", sampleText(900, seed + 3), m2::PACK_TYPE_SNAPPY_XTEA});
    files.push_back({"empty.txt", Bytes(), m2::PACK_TYPE_RAW});
    files.push_back({"locale/game/40k/itemdesc.txt", sampleText(20000, seed + 4), m2::PACK_TYPE_LZO_XTEA});
    return files;
}

bool buildTestPack(const TestSpec& spec, TestPack& out, std::string* err) {
    auto fail = [&](const std::string& m) {
        if (err) *err = m;
        return false;
    };
    const m2::EntryLayout& layout = spec.layout ? *spec.layout : m2::classicLayout();
    out = TestPack();
    out.files = spec.files;

    uint64_t offset = 0;
    std::vector<m2::PackEntry> entries;
    for (size_t i = 0; i < out.files.size(); ++i) {
        const TestFile& f = out.files[i];
        Bytes blob;
        std::string subErr;
        switch (f.type) {
            case m2::PACK_TYPE_RAW:
                blob = f.content;
                break;
            case m2::PACK_TYPE_LZO:
                if (!m2::cryptedObjectEncode(f.content, nullptr, m2::kMagicMCOZ, blob, &subErr))
                    return fail(subErr);
                break;
            case m2::PACK_TYPE_LZO_XTEA:
                if (!m2::cryptedObjectEncode(f.content, &spec.dataKey, m2::kMagicMCOZ, blob, &subErr))
                    return fail(subErr);
                break;
            case m2::PACK_TYPE_SNAPPY_XTEA:
                if (!m2::cryptedObjectEncode(f.content, &spec.dataKey, m2::kMagicMCSP, blob, &subErr))
                    return fail(subErr);
                break;
            default:
                // Types 3/4/5 need server side key material; store the bytes as
                // they are so the reader can be exercised against them.
                blob = f.content;
                break;
        }
        m2::PackEntry e;
        e.id = static_cast<uint32_t>(i);
        e.name = f.name;
        e.nameCrc = m2::crc32(f.name.data(), f.name.size());
        e.realSize = static_cast<uint32_t>(f.content.size());
        e.dataSize = static_cast<uint32_t>(blob.size());
        e.contentCrc = f.content.empty() ? 0 : m2::crc32(f.content.data(), f.content.size());
        e.offset = offset;
        e.type = f.type;
        entries.push_back(e);
        out.epk.insert(out.epk.end(), blob.begin(), blob.end());
        offset += blob.size();
    }

    Bytes blob(12 + layout.stride * entries.size(), 0);
    m2::wr32(blob.data(), m2::kMagicEPKD);
    m2::wr32(blob.data() + 4, 2);
    m2::wr32(blob.data() + 8, static_cast<uint32_t>(entries.size()));
    for (size_t i = 0; i < entries.size(); ++i) {
        const m2::PackEntry& e = entries[i];
        uint8_t* p = blob.data() + 12 + i * layout.stride;
        m2::wr32(p, e.id);
        if (e.name.size() + 1 > layout.nameMax) return fail("test file name too long");
        std::memset(p + layout.nameOff, 0, layout.nameMax);
        std::memcpy(p + layout.nameOff, e.name.data(), e.name.size());
        m2::wr32(p + layout.nameCrcOff, e.nameCrc);
        m2::wr32(p + layout.realSizeOff, e.realSize);
        m2::wr32(p + layout.dataSizeOff, e.dataSize);
        m2::wr32(p + layout.crcOff, e.contentCrc);
        if (layout.offsetSize == 8) m2::wr64(p + layout.offsetOff, e.offset);
        else m2::wr32(p + layout.offsetOff, static_cast<uint32_t>(e.offset));
        p[layout.typeOff] = e.type;
    }

    if (spec.indexMagic == 0) {
        out.eix = blob;
        return true;
    }
    return m2::cryptedObjectEncode(blob, spec.encryptIndex ? &spec.indexKey : nullptr, spec.indexMagic,
                                   out.eix, err);
}

}  // namespace m2test
