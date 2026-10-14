#include <iostream>
#include <fstream>
#include <vector>
#include <cstring>
#include <algorithm>
#include <cctype>
#include "xtea.h"
extern "C" {
#include "lzo/minilzo.h"
}

bool IsHighEntropy16(const uint8_t* data) {
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
    if (printable >= 12) return false;
    return true;
}

int ScoreDecrypted(const uint8_t* data, size_t size) {
    if (size < 16) return 0;
    int score = 0;
    // Check EPKD
    uint32_t magic;
    std::memcpy(&magic, data, 4);
    if (magic == 0x444B5045) score += 100;

    std::string str((char*)data, std::min<size_t>(size, 2048));
    std::string lower = str;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
    const char* keywords[] = {"data/", "pack/", ".mse", ".msm", ".msa", ".txt", ".py", "d:/", "root", "locale", "season", "property", "maps/", "monster", "horse", "item", "weapon", nullptr};
    for (int i = 0; keywords[i]; ++i) {
        if (lower.find(keywords[i]) != std::string::npos) score += 10;
    }
    // Check printable
    int printable = 0;
    for (size_t i = 0; i < std::min<size_t>(size, 1024); ++i) {
        if (data[i] >= 32 && data[i] <= 126) printable++;
    }
    if (printable > 700) score += 5;

    return score;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cout << "Usage: bruteforce <exe> <pack>\n";
        return 1;
    }
    std::string exePath = argv[1];
    std::string packPath = argv[2];

    std::ifstream exeFile(exePath, std::ios::binary | std::ios::ate);
    if (!exeFile) { std::cerr << "Cannot open exe\n"; return 1; }
    size_t exeSize = exeFile.tellg();
    exeFile.seekg(0, std::ios::beg);
    std::vector<uint8_t> exeData(exeSize);
    exeFile.read((char*)exeData.data(), exeSize);
    std::cout << "Exe size: " << exeSize << "\n";

    std::ifstream packFile(packPath, std::ios::binary | std::ios::ate);
    if (!packFile) { std::cerr << "Cannot open pack\n"; return 1; }
    size_t packSize = packFile.tellg();
    packFile.seekg(0, std::ios::beg);
    std::vector<uint8_t> packData(std::min<size_t>(packSize, 8192));
    packFile.read((char*)packData.data(), packData.size());
    std::cout << "Pack size: " << packSize << " testing first " << packData.size() << " bytes\n";

    // Find .data and .rdata
    std::vector<std::pair<size_t,size_t>> ranges;
    if (exeSize > 0x100) {
        uint32_t peOffset = 0;
        std::memcpy(&peOffset, exeData.data() + 0x3C, 4);
        if (peOffset + 6 < exeSize && std::memcmp(exeData.data() + peOffset, "PE\0\0", 4) == 0) {
            uint16_t numSections = 0;
            uint16_t optSize = 0;
            std::memcpy(&numSections, exeData.data() + peOffset + 6, 2);
            std::memcpy(&optSize, exeData.data() + peOffset + 20, 2);
            size_t secStart = peOffset + 24 + optSize;
            for (int i = 0; i < numSections; ++i) {
                size_t off = secStart + i * 40;
                if (off + 40 > exeSize) break;
                char name[9] = {0};
                std::memcpy(name, exeData.data() + off, 8);
                std::string sname = name;
                uint32_t rawSize = 0, rawPtr = 0;
                std::memcpy(&rawSize, exeData.data() + off + 16, 4);
                std::memcpy(&rawPtr, exeData.data() + off + 20, 4);
                if (sname == ".data" || sname == ".rdata") {
                    if (rawPtr + rawSize <= exeSize) {
                        ranges.emplace_back(rawPtr, rawSize);
                        std::cout << "Scanning section " << sname << " at 0x" << std::hex << rawPtr << " size 0x" << rawSize << std::dec << "\n";
                    }
                }
            }
        }
    }
    if (ranges.empty()) {
        ranges.emplace_back(0, std::min<size_t>(exeSize, 20*1024*1024));
    }

    lzo_init();

    int found = 0;
    size_t total = 0;
    for (auto& r : ranges) {
        size_t start = r.first;
        size_t end = start + r.second;
        for (size_t i = start; i + 16 < end; i += 4) {
            total++;
            if (total % 500000 == 0) {
                std::cout << "Scanned " << total << " positions, found " << found << "\n";
            }
            if (!IsHighEntropy16(exeData.data() + i)) continue;

            uint32_t key[4];
            UnpackTool::XTEA::KeyFromBytes(exeData.data() + i, key);

            // Decrypt packData first 1KB
            size_t toDec = (packData.size() / 8) * 8;
            if (toDec < 64) continue;
            std::vector<uint8_t> dec(packData.begin(), packData.begin() + toDec);
            UnpackTool::XTEA::DecryptBuffer(dec, key);

            int score = ScoreDecrypted(dec.data(), dec.size());
            if (score > 0) {
                // Try LZO decompress if score low but maybe compressed
                if (score < 20) {
                    // Try LZO decompress first 1KB decrypted as LZO compressed data
                    // LZO decompress needs output buffer
                    std::vector<uint8_t> out(dec.size() * 4 + 1024);
                    lzo_uint outLen = out.size();
                    lzo_uint inLen = dec.size();
                    int res = lzo1x_decompress_safe(dec.data(), inLen, out.data(), &outLen, nullptr);
                    if (res == LZO_E_OK) {
                        int score2 = ScoreDecrypted(out.data(), outLen);
                        if (score2 > score) score = score2;
                        if (score2 > 10) {
                            std::cout << "[POTENTIAL LZO] offset=0x" << std::hex << i << std::dec << " key=" << UnpackTool::XTEA::KeyToHex(key) << " score=" << score << " score2=" << score2 << "\n";
                            // Print first 200 chars of decompressed
                            std::string s((char*)out.data(), std::min<size_t>(outLen, 200));
                            std::cout << "  Decompressed preview: " << s.substr(0,100) << "\n";
                        }
                    }
                }
                if (score >= 10) {
                    std::cout << "[FOUND] offset=0x" << std::hex << i << std::dec << " key=" << UnpackTool::XTEA::KeyToHex(key) << " score=" << score << "\n";
                    std::string preview((char*)dec.data(), std::min<size_t>(dec.size(), 200));
                    // Replace non-printable with .
                    for (char& c : preview) if (c < 32 || c > 126) c = '.';
                    std::cout << "  Preview: " << preview.substr(0,100) << "\n";
                    found++;
                    if (found >= 20) {
                        std::cout << "Found 20 candidates, stopping\n";
                        return 0;
                    }
                }
            }
        }
    }
    std::cout << "Done, scanned " << total << " positions, found " << found << "\n";
    return 0;
}
