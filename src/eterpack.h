#pragma once
#include <cstdint>
#include <vector>
#include <string>
#include <map>

namespace UnpackTool {

#pragma pack(push, 1)
struct EterPackIndex {
    uint32_t id; // FourCC 'EPKD'
    uint32_t version;
    uint32_t fileCount;
    uint32_t indexStart; // offset where index starts? Or data start?
};

struct EterPackFileEntry {
    char filename[160];
    uint32_t filenameCRC;
    uint32_t dataCRC;
    uint32_t compressedSize;
    uint32_t uncompressedSize;
    uint32_t dataOffset;
    uint8_t  type; // 0 RAW, 1 LZO, 2 XTEA(LZO), 3 Panama, 4/5 HybridCrypt, 6 XTEA(Snappy)
    // plus padding?
};
#pragma pack(pop)

enum class PackFileType : uint8_t {
    RAW = 0,
    LZO = 1,
    XTEA_LZO = 2,
    Panama = 3,
    HybridCrypt = 4,
    HybridCrypt2 = 5,
    XTEA_Snappy = 6,
    Unknown = 255
};

struct PackFileInfo {
    std::string filename;
    uint32_t compressedSize;
    uint32_t uncompressedSize;
    uint32_t dataOffset;
    PackFileType type;
    uint32_t crc;
};

class EterPack {
public:
    EterPack();
    ~EterPack();

    bool Load(const std::string& packPath, const uint32_t indexKey[4], const uint32_t contentKey[4]);
    bool Load(const std::string& packPath, const uint32_t key[4]); // same key for index and content

    const std::vector<PackFileInfo>& GetFileList() const { return fileList; }
    
    bool ExtractFile(const std::string& filename, const std::string& outPath);
    bool ExtractFile(const PackFileInfo& info, const std::string& outPath);
    bool ExtractAll(const std::string& outDir);

    bool ExtractFileToBuffer(const std::string& filename, std::vector<uint8_t>& outData);
    bool ExtractFileToBuffer(const PackFileInfo& info, std::vector<uint8_t>& outData);

    std::string GetPackPath() const { return packPath; }

    // For custom packs like .d2 that may not follow standard EPKD
    bool LoadRaw(const std::string& packPath, const uint32_t key[4]);

private:
    bool ParseIndex(const uint8_t* data, size_t size, const uint32_t key[4]);
    bool DecryptIndex(std::vector<uint8_t>& indexData, const uint32_t key[4]);
    bool DecompressIfNeeded(std::vector<uint8_t>& data, PackFileType type, uint32_t uncompressedSize);
    bool DecryptContent(std::vector<uint8_t>& data, const uint32_t key[4]);

    std::string packPath;
    std::vector<PackFileInfo> fileList;
    std::vector<uint8_t> packData; // memory mapped or loaded? For large files we use file IO
    bool isLoaded;
    uint32_t indexKey[4];
    uint32_t contentKey[4];
    bool useSeparateKeys;

    // File handle for large packs
    FILE* fileHandle;
};

} // namespace UnpackTool
