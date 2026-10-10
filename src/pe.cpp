// SPDX-License-Identifier: MIT
#include "pe.h"

#include <cstring>

namespace m2 {

const PeSection* PeImage::sectionAtFileOffset(uint64_t off) const {
    for (const PeSection& s : sections)
        if (s.containsFileOffset(off)) return &s;
    return nullptr;
}

std::string PeImage::describe() const {
    std::string out = std::string(pe32plus ? "PE32+" : "PE32") + ", machine 0x" +
                      toHex(reinterpret_cast<const uint8_t*>(&machine), 2, "") + ", " +
                      std::to_string(sections.size()) + " sections";
    for (const PeSection& s : sections) {
        out += "\n    " + s.name + "  raw=0x" + toHex(reinterpret_cast<const uint8_t*>(&s.rawPtr), 4, "") +
               " size=" + std::to_string(s.rawSize) + (s.executable() ? " [x]" : "") +
               (s.writable() ? " [w]" : "");
    }
    return out;
}

bool looksLikePe(const uint8_t* data, size_t len) {
    if (len < 0x40 || data[0] != 'M' || data[1] != 'Z') return false;
    const uint32_t lfanew = rd32(data + 0x3C);
    if (lfanew == 0 || lfanew + 4 > len) return false;
    return data[lfanew] == 'P' && data[lfanew + 1] == 'E' && data[lfanew + 2] == 0 && data[lfanew + 3] == 0;
}

bool parsePe(const uint8_t* data, size_t len, PeImage& img, std::string* err) {
    auto fail = [&](const std::string& what) {
        if (err) *err = what;
        return false;
    };
    img = PeImage();
    if (!looksLikePe(data, len)) return fail("not a PE image");

    const uint32_t lfanew = rd32(data + 0x3C);
    const uint8_t* coff = data + lfanew + 4;
    if (lfanew + 4 + 20 > len) return fail("truncated COFF header");

    img.machine = rd16(coff);
    const uint16_t numSections = rd16(coff + 2);
    const uint16_t sizeOfOptional = rd16(coff + 16);
    const uint8_t* opt = coff + 20;
    if (static_cast<size_t>(opt - data) + sizeOfOptional > len) return fail("truncated optional header");

    if (sizeOfOptional >= 2) {
        const uint16_t magic = rd16(opt);
        img.pe32plus = (magic == 0x20B);
        if (magic != 0x10B && magic != 0x20B) return fail("unknown optional header magic");
        img.entryPoint = rd32(opt + 16);
        img.imageBase = img.pe32plus ? rd64(opt + 24) : rd32(opt + 28);
        if (sizeOfOptional >= 60) img.sizeOfImage = rd32(opt + 56);
    }
    // SizeOfImage/SizeOfHeaders sit at the same offset in PE32 and PE32+.
    if (sizeOfOptional >= 64) img.sizeOfHeaders = rd32(opt + 60);

    const uint8_t* sec = opt + sizeOfOptional;
    for (uint16_t i = 0; i < numSections; ++i) {
        const uint8_t* p = sec + static_cast<size_t>(i) * 40;
        if (static_cast<size_t>(p - data) + 40 > len) break;
        PeSection s;
        char nameBuf[9] = {0};
        std::memcpy(nameBuf, p, 8);
        s.name = nameBuf;
        s.virtualSize = rd32(p + 8);
        s.virtualAddress = rd32(p + 12);
        s.rawSize = rd32(p + 16);
        s.rawPtr = rd32(p + 20);
        s.characteristics = rd32(p + 36);
        if (s.rawSize == 0) continue;
        if (s.rawPtr + s.rawSize > len) {
            // Overlays / truncated downloads: keep what is really there.
            if (s.rawPtr >= len) continue;
            s.rawSize = static_cast<uint32_t>(len - s.rawPtr);
        }
        img.sections.push_back(std::move(s));
    }
    img.valid = !img.sections.empty();
    if (!img.valid) return fail("PE image has no usable sections");
    return true;
}

}  // namespace m2
