#pragma once
#include <array>
#include <cstdint>
#include <filesystem>
#include <map>
#include <set>
#include <string>
#include <vector>
namespace history {
namespace fs = std::filesystem;
using Bytes = std::vector<uint8_t>;
constexpr uint32_t Magic = 0xf00fed5c;
constexpr size_t MaxFile = 256u * 1024u * 1024u;
// Directory depth used when a directory is given as an archive source, and when
// assets are auto-discovered next to the executable or the working directory.
constexpr int SearchDepth = 4;
Bytes readFile(const fs::path& path, size_t limit = MaxFile);
std::string normalize(std::string s);
uint32_t nameHash(const std::string& s);
std::string hex32(uint32_t n);
Bytes lz4(const Bytes& input, size_t size);
Bytes decrypt(const Bytes& input, const std::array<uint8_t,32>& key, const std::array<uint8_t,16>& iv);
struct Entry { uint32_t size, checksum, offset, stored, hash; };
class Archive {
    fs::path path_;
public:
    std::array<uint8_t,32> key{};
    std::array<uint8_t,16> iv{};
    std::vector<Entry> entries;
    explicit Archive(const fs::path& path);
    Bytes decode(const Entry& e) const;
};
class Names {
    std::set<uint32_t> wanted_;
    std::map<uint32_t,std::set<std::string>> names_;
public:
    explicit Names(const Archive& a);
    void add(std::string name);
    void scan(const Bytes& data);
    void load(const fs::path& path);
    std::string get(uint32_t hash) const;
    size_t resolved() const;
};
fs::path safeRelative(std::string name);
void writeExclusive(const fs::path& root, const fs::path& relative, const Bytes& data);
// True when the file starts with the History D2 magic and is large enough to
// hold the 68-byte archive header. Never throws.
bool isHistoryArchive(const fs::path& path);
// Every file under `directory` that starts with the History D2 magic, recursive
// up to SearchDepth, de-duplicated and sorted. File names and extensions are
// never trusted, so extension-less Metin2-style packs (PC, monster, locale_de,
// workplace, ...) are found as well as *.d2 files. `directory/pack` is scanned
// first so that the usual primary archive keeps its historical position.
std::vector<fs::path> collectArchives(const fs::path& directory);
// Expands one user-supplied path: a file is used as-is, a directory is scanned.
std::vector<fs::path> resolveArchiveArgument(const fs::path& path);
// Search parents of `start` (and `start/pack`) for History assets. Archives are
// appended to `archives`; the first found executable and name list are returned.
void discoverAssets(const fs::path& start, std::vector<fs::path>& archives,
                    fs::path& exe, fs::path& bundledNames, int levels = 7);
}
