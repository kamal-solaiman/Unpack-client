#include "eterpack.h"
#include "xtea.h"
#include "filetype.h"
#include <fstream>
#include <iostream>
#include <cstring>
#include <filesystem>
#include <algorithm>

extern "C" {
#include "lzo/minilzo.h"
}

namespace UnpackTool {

EterPack::EterPack() : isLoaded(false), useSeparateKeys(false), fileHandle(nullptr) {
    std::memset(indexKey, 0, sizeof(indexKey));
    std::memset(contentKey, 0, sizeof(contentKey));
}

EterPack::~EterPack() {
    if (fileHandle) {
        fclose(fileHandle);
    }
}

bool EterPack::Load(const std::string& path, const uint32_t idxKey[4], const uint32_t cntKey[4]) {
    packPath = path;
    std::memcpy(indexKey, idxKey, sizeof(indexKey));
    std::memcpy(contentKey, cntKey, sizeof(contentKey));
    useSeparateKeys = true;

    std::ifstream file(path, std::ios::binary | std::ios::ate);
    if (!file) {
        std::cerr << "[ERROR] Cannot open pack: " << path << "\n";
        return false;
    }
    size_t fileSize = file.tellg();
    file.seekg(0, std::ios::beg);

    if (fileSize < sizeof(EterPackIndex)) {
        std::cerr << "[ERROR] File too small: " << path << "\n";
        return false;
    }

    // Read header
    EterPackIndex header;
    file.read((char*)&header, sizeof(header));

    // Check magic 'EPKD' = 0x444B5045
    const uint32_t EPKD_MAGIC = 0x444B5045;
    if (header.id != EPKD_MAGIC) {
        // Maybe encrypted header? Try decrypt first 16 bytes with index key
        std::cout << "[INFO] Header magic mismatch (0x" << std::hex << header.id << std::dec << "), trying XTEA decrypt...\n";
        // Read more and try decrypt
        file.seekg(0, std::ios::beg);
        std::vector<uint8_t> firstBytes(1024);
        size_t toRead = std::min<size_t>(fileSize, firstBytes.size());
        file.read((char*)firstBytes.data(), toRead);
        XTEA::DecryptBuffer(firstBytes, indexKey);
        std::memcpy(&header, firstBytes.data(), sizeof(header));
        if (header.id != EPKD_MAGIC) {
            std::cout << "[WARN] Still not EPKD after decrypt, trying raw load mode\n";
            file.close();
            return LoadRaw(path, idxKey);
        } else {
            std::cout << "[INFO] Header decrypted successfully, EPKD found\n";
            // Continue with decrypted approach - need to handle whole file
            file.close();
            return LoadRaw(path, idxKey);
        }
    }

    std::cout << "[INFO] EPKD Header: version=" << header.version << " fileCount=" << header.fileCount << " indexStart=" << header.indexStart << "\n";

    if (header.fileCount == 0 || header.fileCount > 100000) {
        std::cerr << "[ERROR] Invalid file count: " << header.fileCount << "\n";
        return false;
    }

    // Read index
    size_t indexSize = header.fileCount * sizeof(EterPackFileEntry);
    if (header.indexStart + indexSize > fileSize) {
        std::cerr << "[ERROR] Index out of bounds\n";
        return false;
    }

    file.seekg(header.indexStart, std::ios::beg);
    std::vector<uint8_t> indexData(indexSize);
    file.read((char*)indexData.data(), indexSize);

    if (!DecryptIndex(indexData, indexKey)) {
        std::cerr << "[ERROR] Failed to decrypt index\n";
        return false;
    }

    if (!ParseIndex(indexData.data(), indexData.size(), indexKey)) {
        std::cerr << "[ERROR] Failed to parse index\n";
        return false;
    }

    // Keep file handle open for extraction
    fileHandle = fopen(path.c_str(), "rb");
    if (!fileHandle) {
        std::cerr << "[ERROR] Cannot reopen file for extraction\n";
        return false;
    }

    isLoaded = true;
    std::cout << "[INFO] Loaded " << fileList.size() << " files from pack\n";
    return true;
}

bool EterPack::Load(const std::string& path, const uint32_t key[4]) {
    return Load(path, key, key);
}

bool EterPack::DecryptIndex(std::vector<uint8_t>& indexData, const uint32_t key[4]) {
    // Index is XTEA encrypted
    // Each file entry 176 bytes? Let's check size
    // Standard entry is 160+4+4+4+4+4+1 = 181? But packed maybe 176?
    // We'll try decrypt as XTEA blocks
    std::vector<uint8_t> temp = indexData;
    XTEA::DecryptBuffer(temp, key);

    // Check if filenames look valid after decrypt
    // Look for printable strings and common paths
    int validCount = 0;
    size_t entrySize = sizeof(EterPackFileEntry);
    // Try to detect entry size by scanning for valid filenames
    for (size_t i = 0; i + entrySize <= temp.size(); i += entrySize) {
        EterPackFileEntry* entry = (EterPackFileEntry*)(temp.data() + i);
        // Check if filename is printable and contains '/' or '.'
        bool printable = true;
        int slash = 0;
        for (int j = 0; j < 160; ++j) {
            char c = entry->filename[j];
            if (c == '\0') break;
            if (c < 32 || c > 126) { printable = false; break; }
            if (c == '/' || c == '\\' || c == '.') slash++;
        }
        if (printable && slash > 0) validCount++;
    }

    std::cout << "[INFO] Index decrypt check: " << validCount << " valid filenames out of " << temp.size()/entrySize << "\n";

    if (validCount > 0) {
        indexData = temp;
        return true;
    }

    // Try with no decrypt (maybe already plain)
    validCount = 0;
    for (size_t i = 0; i + entrySize <= indexData.size(); i += entrySize) {
        EterPackFileEntry* entry = (EterPackFileEntry*)(indexData.data() + i);
        bool printable = true;
        int slash = 0;
        for (int j = 0; j < 160; ++j) {
            char c = entry->filename[j];
            if (c == '\0') break;
            if (c < 32 || c > 126) { printable = false; break; }
            if (c == '/' || c == '\\' || c == '.') slash++;
        }
        if (printable && slash > 0) validCount++;
    }
    std::cout << "[INFO] Plain index check: " << validCount << " valid\n";
    if (validCount > 0) {
        return true; // already plain
    }

    // Try alternative: maybe filename only is encrypted, not whole entry
    // We'll keep decrypted version anyway
    indexData = temp;
    return true;
}

bool EterPack::ParseIndex(const uint8_t* data, size_t size, const uint32_t key[4]) {
    fileList.clear();
    size_t entrySize = sizeof(EterPackFileEntry);
    size_t count = size / entrySize;

    for (size_t i = 0; i < count; ++i) {
        const EterPackFileEntry* entry = (const EterPackFileEntry*)(data + i * entrySize);
        
        // Skip empty
        if (entry->filename[0] == '\0') continue;
        
        // Validate
        std::string fname(entry->filename, strnlen(entry->filename, 160));
        // Clean up filename (remove garbage after null)
        fname = std::string(entry->filename);

        // Check if filename looks encrypted (non-printable)
        bool isPrintable = true;
        for (char c : fname) {
            if (c != '\0' && (c < 32 || c > 126)) { isPrintable = false; break; }
        }

        if (!isPrintable) {
            // Try decrypt filename with XTEA (filename is 160 bytes, may be encrypted)
            std::vector<uint8_t> fnameBytes(160);
            std::memcpy(fnameBytes.data(), entry->filename, 160);
            XTEA::DecryptBuffer(fnameBytes, key);
            // Try again
            std::string decrypted(fnameBytes.begin(), fnameBytes.end());
            // Find null terminator
            size_t nullPos = decrypted.find('\0');
            if (nullPos != std::string::npos) decrypted = decrypted.substr(0, nullPos);
            // Check if now printable
            bool nowPrintable = true;
            for (char c : decrypted) {
                if (c < 32 || c > 126) { nowPrintable = false; break; }
            }
            if (nowPrintable && !decrypted.empty()) {
                fname = decrypted;
            }
        }

        if (fname.empty()) continue;

        PackFileInfo info;
        info.filename = fname;
        info.compressedSize = entry->compressedSize;
        info.uncompressedSize = entry->uncompressedSize;
        info.dataOffset = entry->dataOffset;
        info.type = (PackFileType)entry->type;
        info.crc = entry->dataCRC;

        // Sanity check sizes
        if (info.compressedSize > 100 * 1024 * 1024) continue; // >100MB likely invalid
        if (info.uncompressedSize > 100 * 1024 * 1024) continue;

        fileList.push_back(info);
    }

    return !fileList.empty();
}

bool EterPack::ExtractFileToBuffer(const std::string& filename, std::vector<uint8_t>& outData) {
    auto it = std::find_if(fileList.begin(), fileList.end(), [&](const PackFileInfo& info) {
        return info.filename == filename;
    });
    if (it == fileList.end()) {
        // Try case insensitive or partial
        for (auto& info : fileList) {
            if (info.filename.find(filename) != std::string::npos) {
                return ExtractFileToBuffer(info, outData);
            }
        }
        return false;
    }
    return ExtractFileToBuffer(*it, outData);
}

bool EterPack::ExtractFileToBuffer(const PackFileInfo& info, std::vector<uint8_t>& outData) {
    // If we have packData in memory (raw mode), use it
    if (!packData.empty() && info.dataOffset == 0) {
        outData = packData;
        return true;
    }

    if (!fileHandle) {
        // Try open
        fileHandle = fopen(packPath.c_str(), "rb");
        if (!fileHandle) return false;
    }

    fseek(fileHandle, info.dataOffset, SEEK_SET);
    std::vector<uint8_t> compressed(info.compressedSize);
    size_t read = fread(compressed.data(), 1, info.compressedSize, fileHandle);
    if (read != info.compressedSize) {
        std::cerr << "[ERROR] Failed to read file data: " << info.filename << "\n";
        return false;
    }

    // Decrypt if needed
    if (info.type == PackFileType::XTEA_LZO || info.type == PackFileType::XTEA_Snappy || info.type == PackFileType::HybridCrypt || info.type == PackFileType::HybridCrypt2) {
        if (!DecryptContent(compressed, contentKey)) {
            std::cerr << "[WARN] Failed to decrypt content for " << info.filename << ", trying as raw\n";
        }
    }

    // Decompress if needed
    if (info.type == PackFileType::LZO || info.type == PackFileType::XTEA_LZO) {
        if (!DecompressIfNeeded(compressed, PackFileType::LZO, info.uncompressedSize)) {
            std::cerr << "[WARN] LZO decompress failed for " << info.filename << "\n";
            // Return as is
            outData = compressed;
            return true;
        }
        outData = compressed;
    } else if (info.type == PackFileType::XTEA_Snappy) {
        // Snappy decompress would happen in DecompressIfNeeded
        outData = compressed;
    } else {
        outData = compressed;
    }

    // If uncompressed size mismatch, try to decompress anyway if data looks compressed
    if (outData.size() != info.uncompressedSize && info.uncompressedSize > 0) {
        // Maybe still compressed
        std::vector<uint8_t> temp = outData;
        if (DecompressIfNeeded(temp, PackFileType::LZO, info.uncompressedSize)) {
            outData = temp;
        }
    }

    return true;
}

bool EterPack::DecryptContent(std::vector<uint8_t>& data, const uint32_t key[4]) {
    XTEA::DecryptBuffer(data, key);
    return true;
}

bool EterPack::DecompressIfNeeded(std::vector<uint8_t>& data, PackFileType type, uint32_t uncompressedSize) {
    if (type != PackFileType::LZO && type != PackFileType::XTEA_LZO) {
        return true; // not LZO
    }

    if (lzo_init() != LZO_E_OK) {
        std::cerr << "[ERROR] LZO init failed\n";
        return false;
    }

    lzo_uint outLen = uncompressedSize;
    if (outLen == 0) outLen = data.size() * 4 + 1024;

    std::vector<uint8_t> out(outLen);
    lzo_uint inLen = data.size();

    int r = lzo1x_decompress_safe(data.data(), inLen, out.data(), &outLen, nullptr);
    if (r != LZO_E_OK) {
        // Try standard
        outLen = out.size();
        r = lzo1x_decompress(data.data(), inLen, out.data(), &outLen, nullptr);
    }

    if (r == LZO_E_OK) {
        out.resize(outLen);
        data = out;
        return true;
    }

    return false;
}

bool EterPack::ExtractFile(const PackFileInfo& info, const std::string& outPath) {
    std::vector<uint8_t> data;
    if (!ExtractFileToBuffer(info, data)) return false;

    // Ensure directory exists
    std::filesystem::path p(outPath);
    std::filesystem::create_directories(p.parent_path());

    // Fix extension if needed
    std::string finalPath = outPath;
    if (finalPath.find(".bin") != std::string::npos || std::filesystem::path(finalPath).extension() == ".bin" || std::filesystem::path(finalPath).extension().empty()) {
        std::string fixedExt = FileTypeDetector::DetectExtension(data, info.filename);
        if (fixedExt != ".bin") {
            // Replace extension
            std::filesystem::path fp(finalPath);
            if (fp.extension() == ".bin") {
                finalPath = fp.replace_extension(fixedExt).string();
            } else if (fp.extension().empty()) {
                finalPath = finalPath + fixedExt;
            }
        }
    }

    std::ofstream out(finalPath, std::ios::binary);
    if (!out) {
        std::cerr << "[ERROR] Cannot write to " << finalPath << "\n";
        return false;
    }
    out.write((char*)data.data(), data.size());
    return true;
}

bool EterPack::ExtractFile(const std::string& filename, const std::string& outPath) {
    auto it = std::find_if(fileList.begin(), fileList.end(), [&](const PackFileInfo& info) {
        return info.filename == filename;
    });
    if (it == fileList.end()) return false;
    return ExtractFile(*it, outPath);
}

bool EterPack::ExtractAll(const std::string& outDir) {
    std::cout << "[INFO] Extracting " << fileList.size() << " files to " << outDir << "\n";
    int success = 0;
    for (auto& info : fileList) {
        std::string outPath = outDir + "/" + info.filename;
        // Fix filename path separators
        std::replace(outPath.begin(), outPath.end(), '\\', '/');
        if (ExtractFile(info, outPath)) {
            success++;
            if (success % 100 == 0) {
                std::cout << "[INFO] Extracted " << success << "/" << fileList.size() << "\n";
            }
        } else {
            std::cerr << "[ERROR] Failed to extract " << info.filename << "\n";
        }
    }
    std::cout << "[INFO] Extraction done: " << success << "/" << fileList.size() << " success\n";
    return success > 0;
}

bool EterPack::LoadRaw(const std::string& path, const uint32_t key[4]) {
    // For .d2 files or custom packs that are just concatenated XTEA encrypted files
    // Try to parse as raw pack: maybe it's EterPack but with encrypted header we already tried
    // Alternative: file is list of files with no index? Or single file?
    // We'll try to treat whole file as single encrypted file
    packPath = path;
    std::memcpy(indexKey, key, sizeof(indexKey));
    std::memcpy(contentKey, key, sizeof(contentKey));

    std::ifstream file(path, std::ios::binary | std::ios::ate);
    if (!file) return false;
    size_t fileSize = file.tellg();
    file.seekg(0, std::ios::beg);
    std::vector<uint8_t> data(fileSize);
    file.read((char*)data.data(), fileSize);

    // Try decrypt whole file
    std::vector<uint8_t> decrypted = data;
    XTEA::DecryptBuffer(decrypted, key);

    // Check if decrypted looks like EPKD
    if (decrypted.size() >= 4) {
        uint32_t magic;
        std::memcpy(&magic, decrypted.data(), 4);
        if (magic == 0x444B5045) {
            std::cout << "[INFO] Raw file decrypted to EPKD, parsing as EterPack\n";
            // Save decrypted to temp and reload
            std::string tempPath = path + ".decrypted.tmp";
            std::ofstream tmp(tempPath, std::ios::binary);
            tmp.write((char*)decrypted.data(), decrypted.size());
            tmp.close();
            bool res = Load(tempPath, key);
            std::filesystem::remove(tempPath);
            return res;
        }
    }

    // Check if it's a single file (like root) that contains many files inside?
    // For now, create a fake entry for the whole file
    fileList.clear();
    PackFileInfo info;
    info.filename = std::filesystem::path(path).filename().string();
    // Try to detect extension after decrypt
    std::string ext = FileTypeDetector::DetectExtension(decrypted, info.filename);
    if (ext != ".bin" && info.filename.find('.') == std::string::npos) {
        info.filename += ext;
    }
    info.compressedSize = fileSize;
    info.uncompressedSize = decrypted.size();
    info.dataOffset = 0;
    info.type = PackFileType::RAW;
    fileList.push_back(info);

    // Save decrypted data for extraction
    // We'll store pack data in memory
    packData = decrypted;
    fileHandle = fopen(path.c_str(), "rb"); // not used for raw, but keep
    isLoaded = true;

    // Override ExtractFileToBuffer for raw mode
    std::cout << "[INFO] Loaded raw file as single entry: " << info.filename << " (" << fileSize << " bytes)\n";
    return true;
}

} // namespace UnpackTool
