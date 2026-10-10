// SPDX-License-Identifier: MIT
// Minimal PE (MZ/COFF) reader - just enough to walk the sections of
// metin2client.exe while hunting for XTEA keys. No Windows headers needed, so
// the tool builds and runs on Linux/macOS too.
#pragma once

#include <cstdint>
#include <string>
#include <vector>

#include "util.h"

namespace m2 {

constexpr uint32_t kScnMemExecute = 0x20000000u;
constexpr uint32_t kScnMemRead = 0x40000000u;
constexpr uint32_t kScnMemWrite = 0x80000000u;
constexpr uint32_t kScnCntCode = 0x00000020u;
constexpr uint32_t kScnCntInitializedData = 0x00000040u;

struct PeSection {
    std::string name;
    uint32_t virtualSize = 0;
    uint32_t virtualAddress = 0;
    uint32_t rawSize = 0;
    uint32_t rawPtr = 0;
    uint32_t characteristics = 0;

    bool readable() const { return (characteristics & kScnMemRead) != 0; }
    bool executable() const { return (characteristics & kScnMemExecute) != 0; }
    bool writable() const { return (characteristics & kScnMemWrite) != 0; }
    bool containsFileOffset(uint64_t off) const {
        return off >= rawPtr && off < rawPtr + static_cast<uint64_t>(rawSize);
    }
};

struct PeImage {
    bool valid = false;
    uint16_t machine = 0;
    bool pe32plus = false;  // PE32+ (64 bit)
    uint64_t imageBase = 0;
    uint32_t entryPoint = 0;
    uint32_t sizeOfHeaders = 0;
    uint32_t sizeOfImage = 0;
    std::vector<PeSection> sections;

    const PeSection* sectionAtFileOffset(uint64_t off) const;
    std::string describe() const;
};

bool looksLikePe(const uint8_t* data, size_t len);
bool parsePe(const uint8_t* data, size_t len, PeImage& img, std::string* err = nullptr);

}  // namespace m2
