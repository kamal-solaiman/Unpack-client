// SPDX-License-Identifier: MIT
// Shared helpers: file IO, little-endian readers, hex, small string utils.
#pragma once

#include <cstdint>
#include <cstring>
#include <optional>
#include <string>
#include <vector>

namespace m2 {

using Bytes = std::vector<uint8_t>;

// ---------------------------------------------------------------- file IO --
std::optional<Bytes> readFile(const std::string& path);
bool writeFile(const std::string& path, const void* data, size_t size);
bool writeFile(const std::string& path, const Bytes& data);
bool writeFile(const std::string& path, const std::string& data);
bool fileExists(const std::string& path);
uint64_t fileSize(const std::string& path);
bool makeDirectories(const std::string& dir);

// Little-endian readers (unaligned safe).
inline uint16_t rd16(const uint8_t* p) {
    uint16_t v;
    std::memcpy(&v, p, 2);
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    v = (uint16_t)((v >> 8) | (v << 8));
#endif
    return v;
}
inline uint32_t rd32(const uint8_t* p) {
    uint32_t v;
    std::memcpy(&v, p, 4);
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    v = __builtin_bswap32(v);
#endif
    return v;
}
inline uint64_t rd64(const uint8_t* p) {
    uint64_t v;
    std::memcpy(&v, p, 8);
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    v = __builtin_bswap64(v);
#endif
    return v;
}
inline void wr16(uint8_t* p, uint16_t v) {
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    v = (uint16_t)((v >> 8) | (v << 8));
#endif
    std::memcpy(p, &v, 2);
}
inline void wr32(uint8_t* p, uint32_t v) {
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    v = __builtin_bswap32(v);
#endif
    std::memcpy(p, &v, 4);
}
inline void wr64(uint8_t* p, uint64_t v) {
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    v = __builtin_bswap64(v);
#endif
    std::memcpy(p, &v, 8);
}

// ------------------------------------------------------------------ text --
std::string toHex(const uint8_t* data, size_t len, const char* sep = " ");
std::string toHex(const Bytes& data, const char* sep = " ");
std::optional<Bytes> fromHex(const std::string& s);

std::string toLower(std::string s);
bool endsWith(const std::string& s, const std::string& suffix);
std::string trim(const std::string& s);
std::vector<std::string> split(const std::string& s, char sep);
std::string joinPath(const std::string& a, const std::string& b);

// Turns a packed file name ("d:/ymir art/xxx", "..\evil", "a\\b") into a safe
// relative path below the output directory. Returns empty string if the name
// cannot be represented safely.
std::string sanitizeVirtualPath(const std::string& name);

// ------------------------------------------------------------------ log ---
enum class LogLevel { Quiet = 0, Normal = 1, Verbose = 2, Debug = 3 };

class Log {
public:
    static LogLevel level;
    static void info(const std::string& msg);     // level >= Normal
    static void verbose(const std::string& msg);  // level >= Verbose
    static void debug(const std::string& msg);    // level >= Debug
    static void warn(const std::string& msg);     // always
    static void error(const std::string& msg);    // always
};

std::string humanSize(uint64_t bytes);
bool stdoutIsTty();

}  // namespace m2
