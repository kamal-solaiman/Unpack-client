// SPDX-License-Identifier: MIT
#include "util.h"

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iostream>

#ifdef _WIN32
#include <io.h>
#else
#include <unistd.h>
#endif

namespace fs = std::filesystem;

namespace m2 {

// ---------------------------------------------------------------- file IO --
std::optional<Bytes> readFile(const std::string& path) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    if (!f) return std::nullopt;
    std::streamoff n = f.tellg();
    if (n < 0) return std::nullopt;
    f.seekg(0, std::ios::beg);
    Bytes out(static_cast<size_t>(n));
    if (n > 0 && !f.read(reinterpret_cast<char*>(out.data()), n)) return std::nullopt;
    return out;
}

bool writeFile(const std::string& path, const void* data, size_t size) {
    std::error_code ec;
    fs::path p(path);
    if (p.has_parent_path()) fs::create_directories(p.parent_path(), ec);
    std::ofstream f(path, std::ios::binary | std::ios::trunc);
    if (!f) return false;
    if (size > 0) f.write(static_cast<const char*>(data), static_cast<std::streamsize>(size));
    return static_cast<bool>(f);
}

bool writeFile(const std::string& path, const Bytes& data) {
    return writeFile(path, data.data(), data.size());
}

bool writeFile(const std::string& path, const std::string& data) {
    return writeFile(path, data.data(), data.size());
}

bool fileExists(const std::string& path) {
    std::error_code ec;
    return fs::exists(path, ec) && fs::is_regular_file(path, ec);
}

uint64_t fileSize(const std::string& path) {
    std::error_code ec;
    auto n = fs::file_size(path, ec);
    if (ec) return 0;
    return static_cast<uint64_t>(n);
}

bool makeDirectories(const std::string& dir) {
    std::error_code ec;
    if (dir.empty()) return false;
    fs::create_directories(dir, ec);
    return !ec;
}

// ------------------------------------------------------------------ text --
static char hexNibble(unsigned v) {
    return static_cast<char>(v < 10 ? '0' + v : 'a' + (v - 10));
}

std::string toHex(const uint8_t* data, size_t len, const char* sep) {
    std::string out;
    const size_t sepLen = sep ? std::strlen(sep) : 0;
    out.reserve(len * (2 + sepLen));
    for (size_t i = 0; i < len; ++i) {
        if (i && sepLen) out += sep;
        out += hexNibble(data[i] >> 4);
        out += hexNibble(data[i] & 0xF);
    }
    return out;
}

std::string toHex(const Bytes& data, const char* sep) {
    return toHex(data.data(), data.size(), sep);
}

std::optional<Bytes> fromHex(const std::string& s) {
    Bytes out;
    int cur = -1;
    for (char c : s) {
        if (std::isspace(static_cast<unsigned char>(c)) || c == ',' || c == ':' || c == '-' || c == '_')
            continue;
        if (c == '0' && cur == -1) {  // tolerate a leading 0x
            cur = 0;
            continue;
        }
        int v;
        if (c >= '0' && c <= '9') v = c - '0';
        else if (c >= 'a' && c <= 'f') v = c - 'a' + 10;
        else if (c >= 'A' && c <= 'F') v = c - 'A' + 10;
        else return std::nullopt;
        if (cur < 0) cur = v;
        else {
            out.push_back(static_cast<uint8_t>((cur << 4) | v));
            cur = -1;
        }
    }
    if (cur > 0) return std::nullopt;  // odd number of nibbles
    return out;
}

std::string toLower(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(),
                   [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
    return s;
}

bool endsWith(const std::string& s, const std::string& suffix) {
    return s.size() >= suffix.size() &&
           std::equal(suffix.rbegin(), suffix.rend(), s.rbegin(),
                      [](char a, char b) { return std::tolower(static_cast<unsigned char>(a)) ==
                                                  std::tolower(static_cast<unsigned char>(b)); });
}

std::string trim(const std::string& s) {
    size_t a = 0, b = s.size();
    while (a < b && std::isspace(static_cast<unsigned char>(s[a]))) ++a;
    while (b > a && std::isspace(static_cast<unsigned char>(s[b - 1]))) --b;
    return s.substr(a, b - a);
}

std::vector<std::string> split(const std::string& s, char sep) {
    std::vector<std::string> out;
    std::string cur;
    for (char c : s) {
        if (c == sep) {
            out.push_back(cur);
            cur.clear();
        } else {
            cur += c;
        }
    }
    out.push_back(cur);
    return out;
}

std::string joinPath(const std::string& a, const std::string& b) {
    if (a.empty()) return b;
    if (b.empty()) return a;
    const char sep =
#ifdef _WIN32
        '\\';
#else
        '/';
#endif
    std::string out = a;
    if (out.back() != '/' && out.back() != '\\') out += sep;
    if (b.front() == '/' || b.front() == '\\') out += b.substr(1);
    else out += b;
    return out;
}

std::string sanitizeVirtualPath(const std::string& name) {
    std::vector<std::string> parts;
    std::string cur;
    for (char c : name) {
        if (c == '/' || c == '\\') {
            parts.push_back(cur);
            cur.clear();
        } else {
            cur += c;
        }
    }
    parts.push_back(cur);

    std::vector<std::string> stack;
    for (std::string p : parts) {
        p = trim(p);
        if (p.empty() || p == ".") continue;
        if (p == "..") {
            if (stack.empty()) return std::string();  // escape attempt
            stack.pop_back();
            continue;
        }
        // Strip a drive prefix such as "d:" and any remaining illegal chars.
        if (p.size() == 2 && p[1] == ':') continue;
        std::string clean;
        for (char c : p) {
            if (c == ':' || c == '*' || c == '?' || c == '"' || c == '<' || c == '>' || c == '|')
                clean += '_';
            else if (static_cast<unsigned char>(c) < 0x20)
                clean += '_';
            else
                clean += c;
        }
        if (clean.empty() || clean == "." || clean == "..") continue;
        stack.push_back(clean);
    }
    if (stack.empty()) return std::string();
    std::string out;
    for (size_t i = 0; i < stack.size(); ++i) {
        if (i) out += '/';
        out += stack[i];
    }
    return out;
}

// ------------------------------------------------------------------ log ---
LogLevel Log::level = LogLevel::Normal;

void Log::info(const std::string& msg) {
    if (level >= LogLevel::Normal) std::cout << msg << '\n';
}
void Log::verbose(const std::string& msg) {
    if (level >= LogLevel::Verbose) std::cout << msg << '\n';
}
void Log::debug(const std::string& msg) {
    if (level >= LogLevel::Debug) std::cout << "[debug] " << msg << '\n';
}
void Log::warn(const std::string& msg) {
    if (level >= LogLevel::Quiet) std::cerr << "[!] " << msg << '\n';
}
void Log::error(const std::string& msg) { std::cerr << "[x] " << msg << '\n'; }

std::string humanSize(uint64_t bytes) {
    static const char* units[] = {"B", "KB", "MB", "GB", "TB"};
    double v = static_cast<double>(bytes);
    int u = 0;
    while (v >= 1024.0 && u < 4) {
        v /= 1024.0;
        ++u;
    }
    char buf[64];
    if (u == 0) std::snprintf(buf, sizeof buf, "%llu B", (unsigned long long)bytes);
    else std::snprintf(buf, sizeof buf, "%.2f %s", v, units[u]);
    return buf;
}

bool stdoutIsTty() {
#ifdef _WIN32
    return ::_isatty(::_fileno(stdout)) != 0;
#else
    return ::isatty(::fileno(stdout)) != 0;
#endif
}

}  // namespace m2
