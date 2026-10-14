#pragma once
#include <cstdint>
#include <vector>
#include <string>

namespace UnpackTool {

struct ExtractedKey {
    uint32_t key[4];
    uint64_t offset; // file offset where found
    std::string hex;
    int score; // confidence
};

class KeyExtractor {
public:
    static std::vector<ExtractedKey> ExtractKeysFromExe(const std::string& exePath);
    static std::vector<ExtractedKey> ScanForHighEntropyKeys(const std::string& exePath);
    static bool TryDecryptPackWithKey(const std::string& packPath, const uint32_t key[4]);

    // Known default keys
    static std::vector<std::vector<uint8_t>> GetDefaultKeys();

    // XTEA delta pattern search
    static std::vector<uint64_t> FindXTEADeltaOffsets(const std::string& exePath);

    // Try to find key via XTEA function analysis (look for mov reg, [rip+disp] near delta)
    static std::vector<ExtractedKey> FindKeysViaXTEAPattern(const std::string& exePath);

private:
    static bool IsHighEntropy16(const uint8_t* data);
    static int ScoreDecryptedData(const uint8_t* data, size_t size);
};

} // namespace UnpackTool
