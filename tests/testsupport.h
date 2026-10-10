// SPDX-License-Identifier: MIT
// Helpers shared by the self tests and by tools/make_fake_client: they build
// synthetic but structurally correct PE images and EterPack archives so the
// whole pipeline (key recovery -> index decrypt -> entry decode) can be
// verified without a real client.
#pragma once

#include <cstdint>
#include <string>
#include <utility>
#include <vector>

#include "eterpack.h"
#include "util.h"
#include "xtea.h"

namespace m2test {

using m2::Bytes;
using m2::XteaKey;

Bytes randomBytes(size_t n, uint32_t seed);
Bytes sampleText(size_t n, uint32_t seed);
XteaKey makeKey(uint32_t a, uint32_t b, uint32_t c, uint32_t d);

// A minimal but valid PE32 image with the given (name, raw data) sections.
Bytes buildPe(const std::vector<std::pair<std::string, Bytes>>& sections);

// Emits four `push imm32` instructions carrying the key dwords, the way a
// compiler materialising a static key array in code would.
void appendPushImmediates(Bytes& code, const XteaKey& key);

struct TestFile {
    std::string name;
    Bytes content;
    uint8_t type;
};

struct TestPack {
    Bytes eix;
    Bytes epk;
    std::vector<TestFile> files;
};

struct TestSpec {
    XteaKey indexKey{};
    XteaKey dataKey{};
    const m2::EntryLayout* layout = nullptr;  // default: the classic 192 byte one
    bool encryptIndex = true;
    uint32_t indexMagic = m2::kMagicMCOZ;  // 0 = write a plain EPKD index
    std::vector<TestFile> files;
};

// Files covering every supported entry type (0, 1, 2, 6) plus an empty one.
std::vector<TestFile> defaultTestFiles(uint32_t seed = 7);

bool buildTestPack(const TestSpec& spec, TestPack& out, std::string* err = nullptr);

}  // namespace m2test
