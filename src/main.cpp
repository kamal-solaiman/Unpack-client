#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <fstream>
#include <algorithm>
#include <cctype>
#include <iomanip>
#include <cstring>

#include "xtea.h"
#include "eterpack.h"
#include "key_extractor.h"
#include "filetype.h"
#include "crypted_object.h"

using namespace UnpackTool;

uint32_t g_indexKey[4] = {0};
uint32_t g_contentKey[4] = {0};
bool g_keysLoaded = false;
std::string g_exePath;
std::string g_packPath;
std::vector<ExtractedKey> g_foundKeys;

void PrintBanner() {
    std::cout << "============================================================\n";
    std::cout << "   UnpackTool - Professional EterPack Decryption System\n";
    std::cout << "   Supports: pack/root, *.eix/*.epk, *.d2, custom packs\n";
    std::cout << "   Features: XTEA key extraction, LZO decompress, filetype fix\n";
    std::cout << "============================================================\n\n";
}

void PrintMenu() {
    std::cout << "\n---------------------- MAIN MENU ----------------------\n";
    std::cout << " 1. Extract XTEA key from exe (auto scan)\n";
    std::cout << " 2. Extract key via XTEA pattern (RIP-relative search)\n";
    std::cout << " 3. List pack files in directory\n";
    std::cout << " 4. Show current keys\n";
    std::cout << " 5. Set custom key manually (hex)\n";
    std::cout << " 6. Load and parse pack (dump file list)\n";
    std::cout << " 7. Decrypt single file by name\n";
    std::cout << " 8. Decrypt all files (extract all)\n";
    std::cout << " 9. Decrypt root/pack file (raw mode, fix .bin)\n";
    std::cout << "10. Fix file extensions in folder (.bin -> correct)\n";
    std::cout << "11. Decrypt filenames (if encrypted)\n";
    std::cout << "12. Brute-force test keys against pack\n";
    std::cout << "13. Show pack info\n";
    std::cout << "14. Decrypt CryptedObject (MCOZ/MCOB/MCSP)\n";
    std::cout << "15. Change exe path\n";
    std::cout << "16. Change pack path\n";
    std::cout << " 0. Exit\n";
    std::cout << "-------------------------------------------------------\n";
    std::cout << " Current EXE: " << (g_exePath.empty() ? "<not set>" : g_exePath) << "\n";
    std::cout << " Current PACK: " << (g_packPath.empty() ? "<not set>" : g_packPath) << "\n";
    std::cout << " Keys loaded: " << (g_keysLoaded ? "YES" : "NO") << "\n";
    if (g_keysLoaded) {
        std::cout << "  Index Key: " << XTEA::KeyToHex(g_indexKey) << "\n";
        std::cout << "  Content Key: " << XTEA::KeyToHex(g_contentKey) << "\n";
    }
    std::cout << "-------------------------------------------------------\n";
    std::cout << "Enter choice: ";
}

std::string Trim(const std::string& s) {
    size_t start = s.find_first_not_of(" \t\r\n");
    if (start == std::string::npos) return "";
    size_t end = s.find_last_not_of(" \t\r\n");
    return s.substr(start, end - start + 1);
}

void SaveKeysToFile() {
    std::ofstream out("keys.txt");
    out << "IndexKey=" << XTEA::KeyToHex(g_indexKey) << "\n";
    out << "ContentKey=" << XTEA::KeyToHex(g_contentKey) << "\n";
    out << "ExePath=" << g_exePath << "\n";
    out.close();
    std::cout << "[INFO] Keys saved to keys.txt\n";
}

void ActionExtractKeys() {
    if (g_exePath.empty()) {
        std::cout << "Enter exe path: ";
        std::string path;
        std::getline(std::cin, path);
        path = Trim(path);
        if (path.empty()) {
            std::cout << "Trying to auto-detect exe in current dir...\n";
            for (auto& p : std::filesystem::directory_iterator(".")) {
                if (p.path().extension() == ".exe") {
                    path = p.path().string();
                    break;
                }
            }
        }
        g_exePath = path;
    }

    if (!std::filesystem::exists(g_exePath)) {
        std::cout << "[ERROR] Exe not found: " << g_exePath << "\n";
        return;
    }

    std::cout << "[INFO] Scanning exe for XTEA keys: " << g_exePath << "\n";
    g_foundKeys = KeyExtractor::ExtractKeysFromExe(g_exePath);

    if (g_foundKeys.empty()) {
        std::cout << "[WARN] No keys found via auto scan\n";
        return;
    }

    std::cout << "\n[INFO] Found " << g_foundKeys.size() << " potential keys:\n";
    for (size_t i = 0; i < g_foundKeys.size() && i < 20; ++i) {
        std::cout << "  [" << i << "] " << g_foundKeys[i].hex << " score=" << g_foundKeys[i].score << " offset=0x" << std::hex << g_foundKeys[i].offset << std::dec << "\n";
    }

    if (!g_foundKeys.empty()) {
        // Use highest score
        std::memcpy(g_indexKey, g_foundKeys[0].key, sizeof(g_indexKey));
        std::memcpy(g_contentKey, g_foundKeys[0].key, sizeof(g_contentKey));
        g_keysLoaded = true;
        std::cout << "[INFO] Auto-selected highest scoring key: " << g_foundKeys[0].hex << "\n";
        SaveKeysToFile();
    }

    std::cout << "Select key index to use (or Enter for auto): ";
    std::string sel;
    std::getline(std::cin, sel);
    sel = Trim(sel);
    if (!sel.empty()) {
        try {
            int idx = std::stoi(sel);
            if (idx >= 0 && idx < (int)g_foundKeys.size()) {
                std::memcpy(g_indexKey, g_foundKeys[idx].key, sizeof(g_indexKey));
                std::memcpy(g_contentKey, g_foundKeys[idx].key, sizeof(g_contentKey));
                g_keysLoaded = true;
                std::cout << "[INFO] Selected key: " << g_foundKeys[idx].hex << "\n";
                SaveKeysToFile();
            }
        } catch (...) {}
    }
}

void ActionExtractKeysPattern() {
    if (g_exePath.empty()) {
        std::cout << "Enter exe path: ";
        std::string path;
        std::getline(std::cin, path);
        g_exePath = Trim(path);
    }
    if (!std::filesystem::exists(g_exePath)) {
        std::cout << "[ERROR] Exe not found\n";
        return;
    }
    std::cout << "[INFO] Searching XTEA pattern (RIP-relative)...\n";
    auto keys = KeyExtractor::FindKeysViaXTEAPattern(g_exePath);
    if (keys.empty()) {
        std::cout << "[WARN] No keys found via pattern\n";
        return;
    }
    for (size_t i = 0; i < keys.size(); ++i) {
        std::cout << "  [" << i << "] " << keys[i].hex << " offset=0x" << std::hex << keys[i].offset << std::dec << "\n";
    }
    std::memcpy(g_indexKey, keys[0].key, sizeof(g_indexKey));
    std::memcpy(g_contentKey, keys[0].key, sizeof(g_contentKey));
    g_keysLoaded = true;
    std::cout << "[INFO] Using key: " << keys[0].hex << "\n";
    SaveKeysToFile();
}

void ActionListPacks() {
    std::string dir;
    std::cout << "Enter directory to scan (empty for current): ";
    std::getline(std::cin, dir);
    dir = Trim(dir);
    if (dir.empty()) dir = ".";
    if (!std::filesystem::exists(dir)) {
        std::cout << "[ERROR] Dir not found\n";
        return;
    }
    std::cout << "[INFO] Scanning " << dir << " for pack files...\n";
    int count = 0;
    for (auto& p : std::filesystem::recursive_directory_iterator(dir)) {
        if (!p.is_regular_file()) continue;
        std::string name = p.path().filename().string();
        std::string ext = p.path().extension().string();
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
        if (ext == ".eix" || ext == ".epk" || ext == ".d2" || name == "root" || name.find("pack") != std::string::npos || ext == ".mix" || ext == ".dat") {
            std::cout << "  " << p.path().string() << " (" << p.file_size() << " bytes)\n";
            count++;
            if (count > 100) { std::cout << "  ... more\n"; break; }
        }
    }
    std::cout << "[INFO] Found " << count << " pack-like files\n";
}

void ActionShowKeys() {
    if (!g_keysLoaded) {
        std::cout << "[INFO] No keys loaded\n";
        // Show defaults
        auto defaults = KeyExtractor::GetDefaultKeys();
        std::cout << "[INFO] Default keys:\n";
        for (auto& k : defaults) {
            uint32_t key[4];
            XTEA::KeyFromBytes(k.data(), key);
            std::cout << "  " << XTEA::KeyToHex(key) << "\n";
        }
        return;
    }
    std::cout << "Index Key: " << XTEA::KeyToHex(g_indexKey) << "\n";
    std::cout << "Content Key: " << XTEA::KeyToHex(g_contentKey) << "\n";
    // Also print as C array
    uint8_t bytes[16];
    XTEA::KeyToBytes(g_indexKey, bytes);
    std::cout << "As bytes: ";
    for (int i = 0; i < 16; ++i) std::cout << "0x" << std::hex << std::setw(2) << std::setfill('0') << (int)bytes[i] << " ";
    std::cout << std::dec << "\n";
}

void ActionSetCustomKey() {
    std::cout << "Enter hex key (32 hex chars, e.g., B99EB0026F69810563989B2879181A00): ";
    std::string hex;
    std::getline(std::cin, hex);
    hex = Trim(hex);
    uint32_t key[4];
    if (!XTEA::ParseHexKey(hex, key)) {
        std::cout << "[ERROR] Invalid hex key, must be 32 hex chars\n";
        return;
    }
    std::memcpy(g_indexKey, key, sizeof(key));
    std::memcpy(g_contentKey, key, sizeof(key));
    g_keysLoaded = true;
    std::cout << "[INFO] Custom key set: " << XTEA::KeyToHex(key) << "\n";

    std::cout << "Also set separate content key? (y/n): ";
    std::string ans;
    std::getline(std::cin, ans);
    if (ans == "y" || ans == "Y") {
        std::cout << "Enter content hex key: ";
        std::string hex2;
        std::getline(std::cin, hex2);
        hex2 = Trim(hex2);
        uint32_t key2[4];
        if (XTEA::ParseHexKey(hex2, key2)) {
            std::memcpy(g_contentKey, key2, sizeof(key2));
            std::cout << "[INFO] Content key set: " << XTEA::KeyToHex(key2) << "\n";
        }
    }
    SaveKeysToFile();
}

void ActionLoadPack() {
    if (!g_keysLoaded) {
        std::cout << "[WARN] No keys loaded, using default keys\n";
        auto defaults = KeyExtractor::GetDefaultKeys();
        if (!defaults.empty()) {
            XTEA::KeyFromBytes(defaults[0].data(), g_indexKey);
            XTEA::KeyFromBytes(defaults[1].data(), g_contentKey);
        }
    }
    if (g_packPath.empty()) {
        std::cout << "Enter pack path (e.g., pack/root or pack/*.epk): ";
        std::string path;
        std::getline(std::cin, path);
        g_packPath = Trim(path);
    }
    if (!std::filesystem::exists(g_packPath)) {
        std::cout << "[ERROR] Pack not found: " << g_packPath << "\n";
        return;
    }

    EterPack pack;
    if (!pack.Load(g_packPath, g_indexKey, g_contentKey)) {
        std::cout << "[ERROR] Failed to load pack, trying raw mode\n";
        if (!pack.LoadRaw(g_packPath, g_indexKey)) {
            std::cout << "[ERROR] Raw mode also failed\n";
            return;
        }
    }

    auto list = pack.GetFileList();
    std::cout << "\n[INFO] Pack contains " << list.size() << " files:\n";
    for (size_t i = 0; i < list.size() && i < 100; ++i) {
        std::cout << "  " << list[i].filename << " size=" << list[i].compressedSize << " type=" << (int)list[i].type << "\n";
    }
    if (list.size() > 100) std::cout << "  ... and " << (list.size() - 100) << " more\n";
}

void ActionDecryptSingle() {
    if (!g_keysLoaded) {
        std::cout << "[ERROR] No keys loaded\n";
        return;
    }
    if (g_packPath.empty()) {
        std::cout << "Enter pack path: ";
        std::string p;
        std::getline(std::cin, p);
        g_packPath = Trim(p);
    }
    std::cout << "Enter filename inside pack to extract (e.g., data/monster/horse.msm): ";
    std::string fname;
    std::getline(std::cin, fname);
    fname = Trim(fname);
    if (fname.empty()) {
        std::cout << "[ERROR] Empty filename\n";
        return;
    }
    std::cout << "Enter output path (empty for ./output/<filename>): ";
    std::string outPath;
    std::getline(std::cin, outPath);
    outPath = Trim(outPath);
    if (outPath.empty()) {
        outPath = "output/" + fname;
    }

    EterPack pack;
    if (!pack.Load(g_packPath, g_indexKey, g_contentKey)) {
        pack.LoadRaw(g_packPath, g_indexKey);
    }

    if (pack.ExtractFile(fname, outPath)) {
        std::cout << "[INFO] Extracted to " << outPath << "\n";
        // Fix extension
        std::vector<uint8_t> data;
        pack.ExtractFileToBuffer(fname, data);
        std::string fixed = FileTypeDetector::FixFileName(outPath, data);
        if (fixed != outPath) {
            std::cout << "[INFO] Fixed extension: " << outPath << " -> " << fixed << "\n";
            try {
                std::filesystem::rename(outPath, fixed);
            } catch (...) {}
        }
    } else {
        std::cout << "[ERROR] Failed to extract " << fname << "\n";
    }
}

void ActionDecryptAll() {
    if (!g_keysLoaded) {
        std::cout << "[ERROR] No keys loaded\n";
        return;
    }
    if (g_packPath.empty()) {
        std::cout << "Enter pack path: ";
        std::string p;
        std::getline(std::cin, p);
        g_packPath = Trim(p);
    }
    std::cout << "Enter output directory (empty for ./output): ";
    std::string outDir;
    std::getline(std::cin, outDir);
    outDir = Trim(outDir);
    if (outDir.empty()) outDir = "output";

    EterPack pack;
    if (!pack.Load(g_packPath, g_indexKey, g_contentKey)) {
        std::cout << "[WARN] Standard load failed, trying raw\n";
        if (!pack.LoadRaw(g_packPath, g_indexKey)) {
            std::cout << "[ERROR] Failed to load pack\n";
            return;
        }
    }

    if (pack.ExtractAll(outDir)) {
        std::cout << "[INFO] All files extracted to " << outDir << "\n";
    } else {
        std::cout << "[ERROR] Extraction failed\n";
    }
}

void ActionDecryptRoot() {
    if (!g_keysLoaded) {
        std::cout << "[ERROR] No keys loaded\n";
        return;
    }
    std::string packPath;
    std::cout << "Enter pack/root or .d2 path: ";
    std::getline(std::cin, packPath);
    packPath = Trim(packPath);
    if (packPath.empty()) packPath = g_packPath;
    if (!std::filesystem::exists(packPath)) {
        std::cout << "[ERROR] File not found\n";
        return;
    }

    std::cout << "[INFO] Decrypting raw file: " << packPath << "\n";
    std::ifstream file(packPath, std::ios::binary | std::ios::ate);
    size_t size = file.tellg();
    file.seekg(0, std::ios::beg);
    std::vector<uint8_t> data(size);
    file.read((char*)data.data(), size);
    file.close();

    std::vector<uint8_t> decrypted = data;
    XTEA::DecryptBuffer(decrypted, g_indexKey);

    // Try to detect if still compressed
    // Check for MCOZ etc
    std::vector<uint8_t> finalData;
    if (CryptedObject::IsCryptedObject(decrypted)) {
        std::cout << "[INFO] Detected CryptedObject, decrypting...\n";
        if (CryptedObject::Decrypt(decrypted, finalData, g_contentKey)) {
            decrypted = finalData;
        }
    }

    std::string ext = FileTypeDetector::DetectExtension(decrypted, packPath);
    std::cout << "[INFO] Detected extension: " << ext << "\n";

    std::string outPath = "output/" + std::filesystem::path(packPath).filename().string();
    if (outPath.find(".bin") != std::string::npos) {
        outPath = outPath.substr(0, outPath.find(".bin")) + ext;
    } else if (std::filesystem::path(outPath).extension() != ext) {
        // If original has no proper ext, add
        if (std::filesystem::path(packPath).extension().string() == "" || std::filesystem::path(packPath).extension() == ".bin") {
            outPath += ext;
        }
    }

    std::filesystem::create_directories(std::filesystem::path(outPath).parent_path());
    std::ofstream out(outPath, std::ios::binary);
    out.write((char*)decrypted.data(), decrypted.size());
    out.close();
    std::cout << "[INFO] Decrypted file saved to " << outPath << " (" << decrypted.size() << " bytes)\n";

    // If file is actually a pack (EPKD), try to extract it
    if (decrypted.size() >= 4) {
        uint32_t magic;
        std::memcpy(&magic, decrypted.data(), 4);
        if (magic == 0x444B5045) {
            std::cout << "[INFO] Decrypted file is EterPack (EPKD), extracting inner files...\n";
            std::string tempPath = outPath + ".tmp";
            std::ofstream tmp(tempPath, std::ios::binary);
            tmp.write((char*)decrypted.data(), decrypted.size());
            tmp.close();
            EterPack inner;
            if (inner.Load(tempPath, g_indexKey, g_contentKey)) {
                inner.ExtractAll("output/" + std::filesystem::path(packPath).filename().string() + "_extracted");
            }
            std::filesystem::remove(tempPath);
        }
    }
}

void ActionFixExtensions() {
    std::string dir;
    std::cout << "Enter folder to fix .bin files (empty for ./output): ";
    std::getline(std::cin, dir);
    dir = Trim(dir);
    if (dir.empty()) dir = "output";
    if (!std::filesystem::exists(dir)) {
        std::cout << "[ERROR] Folder not found\n";
        return;
    }
    int fixed = 0;
    for (auto& p : std::filesystem::recursive_directory_iterator(dir)) {
        if (!p.is_regular_file()) continue;
        if (p.path().extension() == ".bin") {
            std::ifstream file(p.path(), std::ios::binary | std::ios::ate);
            size_t sz = file.tellg();
            file.seekg(0, std::ios::beg);
            std::vector<uint8_t> data(std::min<size_t>(sz, 8192));
            file.read((char*)data.data(), data.size());
            file.close();
            std::string newExt = FileTypeDetector::DetectExtension(data, p.path().filename().string());
            if (newExt != ".bin") {
                std::string newPath = p.path().string();
                newPath = newPath.substr(0, newPath.size() - 4) + newExt;
                try {
                    std::filesystem::rename(p.path(), newPath);
                    std::cout << "[FIX] " << p.path().filename() << " -> " << std::filesystem::path(newPath).filename() << "\n";
                    fixed++;
                } catch (...) {}
            }
        }
    }
    std::cout << "[INFO] Fixed " << fixed << " files\n";
}

void ActionDecryptFilenames() {
    if (!g_keysLoaded) {
        std::cout << "[ERROR] No keys loaded\n";
        return;
    }
    std::cout << "Enter encrypted filename (hex or raw): ";
    std::string name;
    std::getline(std::cin, name);
    name = Trim(name);
    if (name.empty()) return;

    // Try hex decode
    std::vector<uint8_t> data;
    if (name.size() % 2 == 0) {
        bool isHex = true;
        for (char c : name) if (!std::isxdigit(c)) isHex = false;
        if (isHex) {
            for (size_t i = 0; i < name.size(); i += 2) {
                std::string byteStr = name.substr(i, 2);
                uint8_t b = (uint8_t)std::stoi(byteStr, nullptr, 16);
                data.push_back(b);
            }
        }
    }
    if (data.empty()) {
        data.assign(name.begin(), name.end());
    }

    // Pad to multiple of 8
    while (data.size() % 8 != 0) data.push_back(0);

    std::vector<uint8_t> decrypted = data;
    XTEA::DecryptBuffer(decrypted, g_indexKey);
    std::string result((char*)decrypted.data(), decrypted.size());
    // Trim nulls
    result = result.substr(0, result.find('\0'));
    std::cout << "[INFO] Decrypted filename: " << result << "\n";
}

void ActionBruteForce() {
    if (g_packPath.empty()) {
        std::cout << "Enter pack path: ";
        std::string p;
        std::getline(std::cin, p);
        g_packPath = Trim(p);
    }
    if (!std::filesystem::exists(g_packPath)) {
        std::cout << "[ERROR] Pack not found\n";
        return;
    }
    if (g_exePath.empty()) {
        std::cout << "Enter exe path for key scan: ";
        std::string e;
        std::getline(std::cin, e);
        g_exePath = Trim(e);
    }

    std::cout << "[INFO] Brute-forcing keys against pack...\n";
    auto keys = KeyExtractor::ScanForHighEntropyKeys(g_exePath);
    int tested = 0;
    for (auto& k : keys) {
        if (KeyExtractor::TryDecryptPackWithKey(g_packPath, k.key)) {
            std::cout << "[FOUND] Key works: " << k.hex << " score=" << k.score << "\n";
            std::memcpy(g_indexKey, k.key, sizeof(g_indexKey));
            std::memcpy(g_contentKey, k.key, sizeof(g_contentKey));
            g_keysLoaded = true;
            SaveKeysToFile();
            return;
        }
        tested++;
        if (tested % 100 == 0) std::cout << "[INFO] Tested " << tested << " keys...\n";
    }
    std::cout << "[INFO] Tested " << tested << " keys, none worked. Trying defaults...\n";
    auto defaults = KeyExtractor::GetDefaultKeys();
    for (auto& kb : defaults) {
        uint32_t key[4];
        XTEA::KeyFromBytes(kb.data(), key);
        if (KeyExtractor::TryDecryptPackWithKey(g_packPath, key)) {
            std::cout << "[FOUND] Default key works: " << XTEA::KeyToHex(key) << "\n";
            std::memcpy(g_indexKey, key, sizeof(key));
            std::memcpy(g_contentKey, key, sizeof(key));
            g_keysLoaded = true;
            SaveKeysToFile();
            return;
        }
    }
    std::cout << "[FAIL] No working key found\n";
}

void ActionPackInfo() {
    if (g_packPath.empty()) {
        std::cout << "Enter pack path: ";
        std::string p;
        std::getline(std::cin, p);
        g_packPath = Trim(p);
    }
    if (!std::filesystem::exists(g_packPath)) {
        std::cout << "[ERROR] Pack not found\n";
        return;
    }
    std::ifstream file(g_packPath, std::ios::binary | std::ios::ate);
    size_t size = file.tellg();
    file.seekg(0, std::ios::beg);
    std::vector<uint8_t> header(256);
    file.read((char*)header.data(), std::min<size_t>(size, header.size()));
    file.close();

    std::cout << "[INFO] File: " << g_packPath << " Size: " << size << "\n";
    std::cout << "First 16 bytes hex: ";
    for (int i = 0; i < 16 && i < (int)header.size(); ++i) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)header[i] << " ";
    }
    std::cout << std::dec << "\n";

    uint32_t magic;
    std::memcpy(&magic, header.data(), 4);
    std::cout << "Magic as string: " << std::string((char*)header.data(), 4) << " (0x" << std::hex << magic << std::dec << ")\n";

    if (magic == 0x444B5045) {
        std::cout << "[INFO] Detected EterPack (EPKD)\n";
        EterPackIndex* idx = (EterPackIndex*)header.data();
        std::cout << "  Version: " << idx->version << "\n";
        std::cout << "  FileCount: " << idx->fileCount << "\n";
        std::cout << "  IndexStart: " << idx->indexStart << "\n";
    } else {
        std::cout << "[INFO] Not EPKD, checking CryptedObject...\n";
        if (CryptedObject::IsCryptedObject(header)) {
            std::cout << "[INFO] Detected CryptedObject: " << CryptedObject::GetMagicString(magic) << "\n";
            CryptedObjectHeader* hdr = (CryptedObjectHeader*)header.data();
            std::cout << "  CryptedSize: " << hdr->cryptedSize << "\n";
            std::cout << "  CompressedSize: " << hdr->compressedSize << "\n";
            std::cout << "  RealSize: " << hdr->realSize << "\n";
        } else {
            std::cout << "[INFO] Unknown format, trying XTEA decrypt with current key...\n";
            if (g_keysLoaded) {
                std::vector<uint8_t> dec = header;
                XTEA::DecryptBuffer(dec, g_indexKey);
                std::memcpy(&magic, dec.data(), 4);
                std::cout << "After decrypt magic: " << std::string((char*)dec.data(), 4) << " (0x" << std::hex << magic << std::dec << ")\n";
                std::cout << "First 64 bytes after decrypt (as text):\n";
                for (int i = 0; i < 64 && i < (int)dec.size(); ++i) {
                    char c = dec[i];
                    if (c >= 32 && c <= 126) std::cout << c;
                    else std::cout << ".";
                }
                std::cout << "\n";
            }
        }
    }
}

void ActionDecryptCryptedObject() {
    if (!g_keysLoaded) {
        std::cout << "[ERROR] No keys loaded\n";
        return;
    }
    std::string path;
    std::cout << "Enter file path (MCOZ/MCOB file): ";
    std::getline(std::cin, path);
    path = Trim(path);
    if (path.empty()) path = g_packPath;
    if (!std::filesystem::exists(path)) {
        std::cout << "[ERROR] File not found\n";
        return;
    }

    std::ifstream file(path, std::ios::binary | std::ios::ate);
    size_t size = file.tellg();
    file.seekg(0, std::ios::beg);
    std::vector<uint8_t> data(size);
    file.read((char*)data.data(), size);
    file.close();

    std::vector<uint8_t> out;
    if (CryptedObject::Decrypt(data, out, g_contentKey)) {
        std::string ext = FileTypeDetector::DetectExtension(out, path);
        std::string outPath = "output/" + std::filesystem::path(path).filename().string() + ext;
        std::filesystem::create_directories(std::filesystem::path(outPath).parent_path());
        std::ofstream outFile(outPath, std::ios::binary);
        outFile.write((char*)out.data(), out.size());
        outFile.close();
        std::cout << "[INFO] Decrypted to " << outPath << " (" << out.size() << " bytes) ext=" << ext << "\n";
    } else {
        std::cout << "[ERROR] Decrypt failed, trying raw XTEA...\n";
        std::vector<uint8_t> dec = data;
        XTEA::DecryptBuffer(dec, g_contentKey);
        std::string ext = FileTypeDetector::DetectExtension(dec, path);
        std::string outPath = "output/" + std::filesystem::path(path).filename().string() + ext;
        std::filesystem::create_directories(std::filesystem::path(outPath).parent_path());
        std::ofstream outFile(outPath, std::ios::binary);
        outFile.write((char*)dec.data(), dec.size());
        outFile.close();
        std::cout << "[INFO] Raw XTEA decrypted to " << outPath << "\n";
    }
}

int main() {
    PrintBanner();

    // Auto-detect exe and pack
    for (auto& p : std::filesystem::directory_iterator(".")) {
        if (p.path().extension() == ".exe") {
            g_exePath = p.path().string();
            break;
        }
    }
    if (std::filesystem::exists("pack")) {
        for (auto& p : std::filesystem::directory_iterator("pack")) {
            if (p.is_regular_file()) {
                g_packPath = p.path().string();
                break;
            }
        }
    }
    if (g_packPath.empty() && std::filesystem::exists("History/pack")) {
        for (auto& p : std::filesystem::directory_iterator("History/pack")) {
            if (p.is_regular_file()) {
                g_packPath = p.path().string();
                break;
            }
        }
    }

    // Try load keys.txt
    if (std::filesystem::exists("keys.txt")) {
        std::ifstream kf("keys.txt");
        std::string line;
        while (std::getline(kf, line)) {
            if (line.find("IndexKey=") == 0) {
                std::string hex = line.substr(9);
                XTEA::ParseHexKey(hex, g_indexKey);
                g_keysLoaded = true;
            } else if (line.find("ContentKey=") == 0) {
                std::string hex = line.substr(11);
                XTEA::ParseHexKey(hex, g_contentKey);
            }
        }
        std::cout << "[INFO] Loaded keys from keys.txt\n";
    }

    while (true) {
        PrintMenu();
        std::string choiceStr;
        std::getline(std::cin, choiceStr);
        choiceStr = Trim(choiceStr);
        if (choiceStr.empty()) continue;
        int choice = -1;
        try { choice = std::stoi(choiceStr); } catch (...) { continue; }

        switch (choice) {
            case 1: ActionExtractKeys(); break;
            case 2: ActionExtractKeysPattern(); break;
            case 3: ActionListPacks(); break;
            case 4: ActionShowKeys(); break;
            case 5: ActionSetCustomKey(); break;
            case 6: ActionLoadPack(); break;
            case 7: ActionDecryptSingle(); break;
            case 8: ActionDecryptAll(); break;
            case 9: ActionDecryptRoot(); break;
            case 10: ActionFixExtensions(); break;
            case 11: ActionDecryptFilenames(); break;
            case 12: ActionBruteForce(); break;
            case 13: ActionPackInfo(); break;
            case 14: ActionDecryptCryptedObject(); break;
            case 15: {
                std::cout << "Enter new exe path: ";
                std::string p;
                std::getline(std::cin, p);
                g_exePath = Trim(p);
                break;
            }
            case 16: {
                std::cout << "Enter new pack path: ";
                std::string p;
                std::getline(std::cin, p);
                g_packPath = Trim(p);
                break;
            }
            case 0: {
                std::cout << "Exiting...\n";
                return 0;
            }
            default: std::cout << "Invalid choice\n"; break;
        }
    }

    return 0;
}
