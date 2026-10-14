#include "key_extractor.h"
#include "xtea.h"
#include <fstream>
#include <iostream>
#include <cstring>
#include <algorithm>
#include <cctype>
#include <filesystem>

namespace UnpackTool {

std::vector<std::vector<uint8_t>> KeyExtractor::GetDefaultKeys() {
    return {
        // Index key
        {0xB9, 0x9E, 0xB0, 0x02, 0x6F, 0x69, 0x81, 0x05, 0x63, 0x98, 0x9B, 0x28, 0x79, 0x18, 0x1A, 0x00},
        // Content key
        {0x22, 0xB8, 0xB4, 0x04, 0x64, 0xB2, 0x6E, 0x1F, 0xAE, 0xEA, 0x18, 0x00, 0xA6, 0xF6, 0xFB, 0x1C},
        // Custom
        {0x54, 0xD8, 0x20, 0x39, 0xAA, 0x8D, 0x27, 0x22, 0xDC, 0x23, 0xE8, 0x1C, 0x69, 0x6B, 0x74, 0x30}
    };
}

std::vector<uint64_t> KeyExtractor::FindXTEADeltaOffsets(const std::string& exePath) {
    std::vector<uint64_t> offsets;
    std::ifstream file(exePath, std::ios::binary | std::ios::ate);
    if (!file) return offsets;
    size_t size = file.tellg();
    file.seekg(0, std::ios::beg);
    std::vector<uint8_t> data(size);
    file.read((char*)data.data(), size);

    // XTEA delta 0x9E3779B9 little endian: B9 79 37 9E
    const uint8_t deltaLE[4] = {0xB9, 0x79, 0x37, 0x9E};
    const uint8_t deltaBE[4] = {0x9E, 0x37, 0x79, 0xB9};

    for (size_t i = 0; i + 4 < size; ++i) {
        if (std::memcmp(data.data() + i, deltaLE, 4) == 0 || std::memcmp(data.data() + i, deltaBE, 4) == 0) {
            offsets.push_back(i);
        }
    }
    std::cout << "[INFO] Found " << offsets.size() << " XTEA delta occurrences\n";
    return offsets;
}

bool KeyExtractor::IsHighEntropy16(const uint8_t* data) {
    int zeroCount = 0;
    int distinct = 0;
    bool seen[256] = {false};
    int printable = 0;
    for (int i = 0; i < 16; ++i) {
        if (data[i] == 0) zeroCount++;
        if (!seen[data[i]]) { seen[data[i]] = true; distinct++; }
        if (data[i] >= 32 && data[i] <= 126) printable++;
    }
    if (zeroCount >= 8) return false;
    if (distinct < 8) return false;
    if (printable >= 12) return false; // likely string
    return true;
}

int KeyExtractor::ScoreDecryptedData(const uint8_t* data, size_t size) {
    if (size < 16) return 0;
    int score = 0;
    std::string str((char*)data, std::min<size_t>(size, 1024));
    std::string lower = str;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    // Look for EPKD magic
    if (size >= 4) {
        uint32_t magic;
        std::memcpy(&magic, data, 4);
        if (magic == 0x444B5045) score += 100; // EPKD
    }

    // Look for common Metin2 paths
    const char* keywords[] = {"data/", "pack/", ".mse", ".msm", ".msa", ".txt", ".py", "d:/", "root", "locale", "season", "property", "maps/", nullptr};
    for (int i = 0; keywords[i]; ++i) {
        if (lower.find(keywords[i]) != std::string::npos) score += 10;
    }

    // Check printable ratio
    int printable = 0;
    int nulls = 0;
    for (size_t i = 0; i < std::min<size_t>(size, 1024); ++i) {
        if (data[i] >= 32 && data[i] <= 126) printable++;
        if (data[i] == 0) nulls++;
    }
    if (printable > 700) score += 5;
    if (nulls > 0 && nulls < 100) score += 2;

    // Check for file extensions
    if (lower.find(".dds") != std::string::npos) score += 5;
    if (lower.find(".tga") != std::string::npos) score += 5;

    return score;
}

std::vector<ExtractedKey> KeyExtractor::ScanForHighEntropyKeys(const std::string& exePath) {
    std::vector<ExtractedKey> results;
    std::ifstream file(exePath, std::ios::binary | std::ios::ate);
    if (!file) return results;
    size_t size = file.tellg();
    file.seekg(0, std::ios::beg);
    std::vector<uint8_t> data(size);
    file.read((char*)data.data(), size);

    // Parse PE to get .data/.rdata sections only for faster scan
    std::vector<std::pair<size_t, size_t>> scanRanges; // file offset, size
    if (size > 0x100) {
        uint32_t peOffset = 0;
        std::memcpy(&peOffset, data.data() + 0x3C, 4);
        if (peOffset + 6 < size && std::memcmp(data.data() + peOffset, "PE\0\0", 4) == 0) {
            uint16_t numSections = 0;
            uint16_t optHeaderSize = 0;
            std::memcpy(&numSections, data.data() + peOffset + 6, 2);
            std::memcpy(&optHeaderSize, data.data() + peOffset + 20, 2);
            size_t sectionHeaderStart = peOffset + 24 + optHeaderSize;
            for (int i = 0; i < numSections; ++i) {
                size_t off = sectionHeaderStart + i * 40;
                if (off + 40 > size) break;
                char name[9] = {0};
                std::memcpy(name, data.data() + off, 8);
                std::string secName = name;
                uint32_t rawSize = 0, rawPtr = 0;
                std::memcpy(&rawSize, data.data() + off + 16, 4);
                std::memcpy(&rawPtr, data.data() + off + 20, 4);
                if (secName == ".data" || secName == ".rdata" || secName == ".rsrc" || secName.find("data") != std::string::npos) {
                    if (rawPtr + rawSize <= size) {
                        scanRanges.emplace_back(rawPtr, rawSize);
                        std::cout << "[INFO] Will scan section " << secName << " at 0x" << std::hex << rawPtr << " size 0x" << rawSize << std::dec << "\n";
                    }
                }
            }
        }
    }
    if (scanRanges.empty()) {
        // Fallback: scan whole file but with 4-byte alignment and limited to first 20MB for speed
        size_t scanSize = std::min<size_t>(size, 20 * 1024 * 1024);
        scanRanges.emplace_back(0, scanSize);
        std::cout << "[INFO] No data sections found, scanning first " << scanSize << " bytes\n";
    }

    // We need pack file to test against, try to find pack files near exe
    std::filesystem::path exeDir = std::filesystem::path(exePath).parent_path();
    std::vector<std::string> packCandidates;
    try {
        for (auto& p : std::filesystem::directory_iterator(exeDir)) {
            if (p.is_regular_file()) {
                std::string ext = p.path().extension().string();
                std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
                if (ext == ".eix" || ext == ".epk" || ext == ".d2" || p.path().filename() == "root" || p.path().filename().string().find("pack") != std::string::npos) {
                    packCandidates.push_back(p.path().string());
                }
            }
        }
        // Also check pack/ subdir
        std::filesystem::path packDir = exeDir / "pack";
        if (std::filesystem::exists(packDir)) {
            for (auto& p : std::filesystem::directory_iterator(packDir)) {
                if (p.is_regular_file()) packCandidates.push_back(p.path().string());
            }
        }
    } catch (...) {}

    if (packCandidates.empty()) {
        std::cout << "[WARN] No pack files found for testing, will only list high entropy blocks\n";
    }

    std::string testPack = packCandidates.empty() ? "" : packCandidates[0];
    std::vector<uint8_t> testData;
    if (!testPack.empty()) {
        std::ifstream pf(testPack, std::ios::binary | std::ios::ate);
        if (pf) {
            size_t ps = pf.tellg();
            pf.seekg(0, std::ios::beg);
            testData.resize(std::min<size_t>(ps, 4096));
            pf.read((char*)testData.data(), testData.size());
            std::cout << "[INFO] Using test pack: " << testPack << " (" << ps << " bytes)\n";
        }
    }

    size_t totalScanned = 0;
    for (auto& range : scanRanges) {
        size_t start = range.first;
        size_t end = start + range.second;
        if (end > size) end = size;
        for (size_t i = start; i + 16 < end; i += 4) { // 4-byte aligned for speed
            totalScanned++;
            if (totalScanned % 1000000 == 0) {
                std::cout << "[INFO] Scanned " << totalScanned << " positions, found " << results.size() << " candidates...\n";
            }
            if (!IsHighEntropy16(data.data() + i)) continue;

            uint32_t key[4];
            XTEA::KeyFromBytes(data.data() + i, key);

            int score = 0;
            if (!testData.empty()) {
                // Decrypt first 1KB
                size_t toDecrypt = std::min<size_t>(testData.size(), 1024);
                toDecrypt = (toDecrypt / 8) * 8;
                if (toDecrypt >= 16) {
                    std::vector<uint8_t> temp(testData.begin(), testData.begin() + toDecrypt);
                    XTEA::DecryptBuffer(temp, key);
                    score = ScoreDecryptedData(temp.data(), temp.size());
                }
            } else {
                score = 1; // no test data, keep as potential
            }

            if (score > 5) {
                ExtractedKey ek;
                std::memcpy(ek.key, key, sizeof(ek.key));
                ek.offset = i;
                ek.hex = XTEA::KeyToHex(key);
                ek.score = score;
                results.push_back(ek);
                if (results.size() > 200) {
                    // Sort and keep top 100
                    std::sort(results.begin(), results.end(), [](const ExtractedKey& a, const ExtractedKey& b){ return a.score > b.score; });
                    results.resize(100);
                }
            }
        }
    }

    // Sort by score
    std::sort(results.begin(), results.end(), [](const ExtractedKey& a, const ExtractedKey& b) {
        return a.score > b.score;
    });

    if (results.size() > 100) results.resize(100);

    std::cout << "[INFO] Found " << results.size() << " potential keys via high entropy scan (scanned " << totalScanned << " positions)\n";
    return results;
}

std::vector<ExtractedKey> KeyExtractor::FindKeysViaXTEAPattern(const std::string& exePath) {
    std::vector<ExtractedKey> results;
    std::ifstream file(exePath, std::ios::binary | std::ios::ate);
    if (!file) return results;
    size_t fileSize = file.tellg();
    file.seekg(0, std::ios::beg);
    std::vector<uint8_t> data(fileSize);
    file.read((char*)data.data(), fileSize);

    // Search for XTEA pattern: look for instructions near delta
    // We search for delta and then look nearby for potential key loads
    // In x64: mov reg, [rip+disp] where disp points to .data containing key
    // For simplicity, we look for 16-byte aligned data in .data section that could be key, near delta references

    // Parse PE to find sections (simplified)
    // DOS header at 0, PE header offset at 0x3C
    if (fileSize < 0x100) return results;
    uint32_t peOffset;
    std::memcpy(&peOffset, data.data() + 0x3C, 4);
    if (peOffset + 6 > fileSize) return results;

    // Check PE signature
    if (std::memcmp(data.data() + peOffset, "PE\0\0", 4) != 0) return results;

    uint16_t numSections;
    std::memcpy(&numSections, data.data() + peOffset + 6, 2);
    uint16_t optHeaderSize;
    std::memcpy(&optHeaderSize, data.data() + peOffset + 20, 2);

    size_t sectionHeaderStart = peOffset + 24 + optHeaderSize;
    std::cout << "[INFO] PE sections: " << numSections << " optSize=" << optHeaderSize << "\n";

    struct Section {
        std::string name;
        uint32_t vSize;
        uint32_t vAddr;
        uint32_t rawSize;
        uint32_t rawPtr;
    };
    std::vector<Section> sections;

    for (int i = 0; i < numSections; ++i) {
        size_t off = sectionHeaderStart + i * 40;
        if (off + 40 > fileSize) break;
        char name[9] = {0};
        std::memcpy(name, data.data() + off, 8);
        Section s;
        s.name = name;
        std::memcpy(&s.vSize, data.data() + off + 8, 4);
        std::memcpy(&s.vAddr, data.data() + off + 12, 4);
        std::memcpy(&s.rawSize, data.data() + off + 16, 4);
        std::memcpy(&s.rawPtr, data.data() + off + 20, 4);
        sections.push_back(s);
        std::cout << "[INFO] Section " << s.name << " VA=0x" << std::hex << s.vAddr << " rawPtr=0x" << s.rawPtr << " rawSize=0x" << s.rawSize << std::dec << "\n";
    }

    // Find .text section
    Section* textSec = nullptr;
    Section* dataSec = nullptr;
    Section* rdataSec = nullptr;
    for (auto& s : sections) {
        if (s.name == ".text") textSec = &s;
        if (s.name == ".data") dataSec = &s;
        if (s.name == ".rdata") rdataSec = &s;
    }

    if (!textSec) {
        std::cout << "[WARN] No .text section found\n";
        return results;
    }

    // Search in .text for delta
    size_t textStart = textSec->rawPtr;
    size_t textEnd = textStart + textSec->rawSize;
    if (textEnd > fileSize) textEnd = fileSize;

    std::vector<size_t> deltaOffsets;
    const uint8_t deltaLE[4] = {0xB9, 0x79, 0x37, 0x9E};
    for (size_t i = textStart; i + 4 < textEnd; ++i) {
        if (std::memcmp(data.data() + i, deltaLE, 4) == 0) {
            deltaOffsets.push_back(i);
        }
    }
    std::cout << "[INFO] Found " << deltaOffsets.size() << " deltas in .text\n";

    // For each delta, look backwards up to 200 bytes for RIP-relative loads (x64) or absolute (x86)
    // Pattern x64: 48 8D ?? ?? ?? ?? ??  or 4C 8D etc, and also 48 8B 0D disp32
    // We'll look for 0x8B 0x0D or 0x8B 0x1D etc (mov reg, [rip+disp])
    for (size_t deltaOff : deltaOffsets) {
        size_t searchStart = deltaOff > 200 ? deltaOff - 200 : textStart;
        for (size_t j = searchStart; j + 7 < deltaOff; ++j) {
            // Check for mov reg, [rip+disp] - opcode 0x8B with ModRM 0x0D, 0x1D, 0x2D, 0x3D etc
            uint8_t b1 = data[j];
            uint8_t b2 = data[j+1];
            uint8_t b3 = data[j+2];
            // Simple pattern: 8B 0D/1D/2D/3D/05 disp32
            if (b1 == 0x8B && (b2 == 0x0D || b2 == 0x1D || b2 == 0x2D || b2 == 0x3D || b2 == 0x05)) {
                int32_t disp;
                std::memcpy(&disp, data.data() + j + 2, 4);
                // RIP is next instruction after this 6-byte instruction
                size_t nextRip = j + 6;
                // Convert file offset to VA: VA = rawPtr->vAddr mapping
                // For .text, fileOffset = rawPtr + (VA - vAddr)
                // So VA = vAddr + (fileOffset - rawPtr)
                uint64_t instrVA = textSec->vAddr + (j - textSec->rawPtr);
                uint64_t targetVA = instrVA + 6 + disp;
                // Find which section contains targetVA
                for (auto& sec : sections) {
                    if (targetVA >= sec.vAddr && targetVA < sec.vAddr + sec.vSize) {
                        size_t targetFileOff = sec.rawPtr + (targetVA - sec.vAddr);
                        if (targetFileOff + 16 <= fileSize) {
                            if (IsHighEntropy16(data.data() + targetFileOff)) {
                                uint32_t key[4];
                                XTEA::KeyFromBytes(data.data() + targetFileOff, key);
                                ExtractedKey ek;
                                std::memcpy(ek.key, key, sizeof(key));
                                ek.offset = targetFileOff;
                                ek.hex = XTEA::KeyToHex(key);
                                ek.score = 50; // high confidence via pattern
                                results.push_back(ek);
                                std::cout << "[INFO] Found potential key via RIP-relative at file offset 0x" << std::hex << targetFileOff << " VA=0x" << targetVA << " hex=" << ek.hex << std::dec << "\n";
                            }
                        }
                    }
                }
            }
        }
    }

    // Deduplicate
    std::sort(results.begin(), results.end(), [](const ExtractedKey& a, const ExtractedKey& b){ return a.hex < b.hex; });
    results.erase(std::unique(results.begin(), results.end(), [](const ExtractedKey& a, const ExtractedKey& b){ return a.hex == b.hex; }), results.end());

    return results;
}

std::vector<ExtractedKey> KeyExtractor::ExtractKeysFromExe(const std::string& exePath) {
    std::vector<ExtractedKey> all;
    auto viaPattern = FindKeysViaXTEAPattern(exePath);
    all.insert(all.end(), viaPattern.begin(), viaPattern.end());
    auto viaEntropy = ScanForHighEntropyKeys(exePath);
    all.insert(all.end(), viaEntropy.begin(), viaEntropy.end());

    // Add defaults with high score if they work?
    // Deduplicate
    std::sort(all.begin(), all.end(), [](const ExtractedKey& a, const ExtractedKey& b){ return a.hex < b.hex; });
    all.erase(std::unique(all.begin(), all.end(), [](const ExtractedKey& a, const ExtractedKey& b){ return a.hex == b.hex; }), all.end());

    // Sort by score descending
    std::sort(all.begin(), all.end(), [](const ExtractedKey& a, const ExtractedKey& b){ return a.score > b.score; });

    return all;
}

bool KeyExtractor::TryDecryptPackWithKey(const std::string& packPath, const uint32_t key[4]) {
    std::ifstream file(packPath, std::ios::binary | std::ios::ate);
    if (!file) return false;
    size_t size = file.tellg();
    file.seekg(0, std::ios::beg);
    std::vector<uint8_t> data(std::min<size_t>(size, 4096));
    file.read((char*)data.data(), data.size());
    std::vector<uint8_t> decrypted = data;
    size_t toDecrypt = (decrypted.size() / 8) * 8;
    if (toDecrypt < 16) return false;
    decrypted.resize(toDecrypt);
    XTEA::DecryptBuffer(decrypted, key);
    int score = ScoreDecryptedData(decrypted.data(), decrypted.size());
    return score > 10;
}

} // namespace UnpackTool
