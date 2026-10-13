// Standalone ALT2 archive verifier and extractor.
// Built with Visual Studio 2022 (x64, C++17); no third-party libraries are required.
// It never executes the supplied client or any extracted file.

#include <algorithm>
#include <array>
#include <charconv>
#include <chrono>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>
#include <vector>

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#else
#include <cerrno>
#include <fcntl.h>
#include <sys/types.h>
#include <unistd.h>
#if defined(__linux__)
#include <sys/syscall.h>
#ifndef RENAME_NOREPLACE
#define RENAME_NOREPLACE (1 << 0)
#endif
#endif
#endif

namespace alt2 {
namespace fs = std::filesystem;
using Bytes = std::vector<std::uint8_t>;

constexpr std::uint32_t kMagic = 0x000FED0Cu;
constexpr std::uint32_t kXteaDelta = 0x9E3779B9u;
constexpr std::uint64_t kDefaultMaxFileSize = 128ull * 1024ull * 1024ull;
constexpr std::uint64_t kDefaultMaxTotalSize = 1024ull * 1024ull * 1024ull;
constexpr std::size_t kHeaderSize = 24;
constexpr std::size_t kMaxEntries = 1'000'000;

// Deterministic name-generation caps; the Python reference implementation
// (alt2/unpack.py, NameResolver) must keep exactly the same values and order.
constexpr std::size_t kDirectoryLimit = 2048;
constexpr std::size_t kBareFragmentLimit = 16384;
constexpr std::size_t kTokenLimit = 262144;
constexpr std::size_t kStemDirectoryLimit = 600;
constexpr std::uint64_t kDirectoryCombinationLimit = 4'000'000ull;

constexpr std::array<std::string_view, 34> kAllExtensions{{
    ".pyc", ".pyo", ".py", ".msm", ".msa", ".mse", ".msf", ".txt", ".xml", ".json",
    ".cfg", ".ini", ".sub", ".dds", ".tga", ".png", ".jpg", ".jpeg", ".bmp", ".psd",
    ".gr2", ".wav", ".mp3", ".ogg", ".avi", ".ttf", ".otf", ".def", ".bin", ".dat",
    ".sct", ".atr", ".raw", ".wtr"}};
constexpr std::array<std::string_view, 15> kTokenExtensions{{
    ".pyc", ".py", ".msm", ".msa", ".txt", ".xml", ".dds", ".tga", ".png", ".jpg",
    ".bmp", ".gr2", ".wav", ".ogg", ".avi"}};
constexpr std::array<std::string_view, 8> kStemExtensions{{
    ".png", ".tga", ".dds", ".jpg", ".py", ".wav", ".ogg", ".txt"}};
constexpr std::string_view kStemCharacters = "abcdefghijklmnopqrstuvwxyz0123456789_";

class UnpackError : public std::runtime_error {
public:
    explicit UnpackError(const std::string& message) : std::runtime_error(message) {}
};

std::uint16_t read_u16(const Bytes& data, std::size_t offset) {
    if (offset > data.size() || data.size() - offset < 2) {
        throw UnpackError("Truncated integer while parsing client executable");
    }
    return static_cast<std::uint16_t>(data[offset]) |
           static_cast<std::uint16_t>(static_cast<std::uint16_t>(data[offset + 1]) << 8);
}

std::uint32_t read_u32(const Bytes& data, std::size_t offset) {
    if (offset > data.size() || data.size() - offset < 4) {
        throw UnpackError("Truncated integer while parsing input");
    }
    return static_cast<std::uint32_t>(data[offset]) |
           (static_cast<std::uint32_t>(data[offset + 1]) << 8) |
           (static_cast<std::uint32_t>(data[offset + 2]) << 16) |
           (static_cast<std::uint32_t>(data[offset + 3]) << 24);
}

std::uint32_t read_u32_ptr(const std::uint8_t* p) {
    return static_cast<std::uint32_t>(p[0]) |
           (static_cast<std::uint32_t>(p[1]) << 8) |
           (static_cast<std::uint32_t>(p[2]) << 16) |
           (static_cast<std::uint32_t>(p[3]) << 24);
}

std::uint64_t read_u64(const Bytes& data, std::size_t offset) {
    if (offset > data.size() || data.size() - offset < 8) {
        throw UnpackError("Truncated integer while parsing client executable");
    }
    std::uint64_t value = 0;
    for (unsigned i = 0; i != 8; ++i) {
        value |= static_cast<std::uint64_t>(data[offset + i]) << (8 * i);
    }
    return value;
}

void write_u32(Bytes& data, std::size_t offset, std::uint32_t value) {
    if (offset > data.size() || data.size() - offset < 4) {
        throw UnpackError("Internal self-test buffer error");
    }
    for (unsigned i = 0; i != 4; ++i) {
        data[offset + i] = static_cast<std::uint8_t>(value >> (8 * i));
    }
}

std::string hex_u32(std::uint32_t value) {
    std::ostringstream out;
    out << "0x" << std::hex << std::nouppercase << std::setw(8) << std::setfill('0') << value;
    return out.str();
}

std::string hex_u64(std::uint64_t value) {
    std::ostringstream out;
    out << "0x" << std::hex << std::nouppercase << value;
    return out.str();
}

std::string hex_bytes(const std::uint8_t* data, std::size_t size) {
    static constexpr char digits[] = "0123456789abcdef";
    std::string result;
    result.resize(size * 2);
    for (std::size_t i = 0; i < size; ++i) {
        result[i * 2] = digits[data[i] >> 4];
        result[i * 2 + 1] = digits[data[i] & 0x0F];
    }
    return result;
}

std::string json_escape(std::string_view text) {
    std::string out;
    out.reserve(text.size() + 8);
    for (unsigned char c : text) {
        switch (c) {
        case '"': out += "\\\""; break;
        case '\\': out += "\\\\"; break;
        case '\b': out += "\\b"; break;
        case '\f': out += "\\f"; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default:
            if (c < 0x20) {
                static constexpr char digits[] = "0123456789abcdef";
                out += "\\u00";
                out += digits[c >> 4];
                out += digits[c & 0x0F];
            } else {
                out += static_cast<char>(c);
            }
        }
    }
    return out;
}

std::string path_utf8(const fs::path& path) {
    const auto text = path.generic_u8string();
    return std::string(text.begin(), text.end());
}

fs::path path_from_utf8(const std::string& text) {
    return fs::u8path(text.begin(), text.end());
}

Bytes read_file(const fs::path& path) {
    std::error_code ec;
    const auto length = fs::file_size(path, ec);
    if (ec) {
        throw UnpackError("Cannot read file size for " + path_utf8(path) + ": " + ec.message());
    }
    if (length > static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
        throw UnpackError("File is too large for this build: " + path_utf8(path));
    }
    std::ifstream stream(path, std::ios::binary);
    if (!stream) {
        throw UnpackError("Cannot open file: " + path_utf8(path));
    }
    Bytes data(static_cast<std::size_t>(length));
    if (!data.empty()) {
        stream.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(data.size()));
        if (stream.gcount() != static_cast<std::streamsize>(data.size())) {
            throw UnpackError("Short read from file: " + path_utf8(path));
        }
    }
    return data;
}

void write_file(const fs::path& path, const Bytes& data) {
    std::ofstream stream(path, std::ios::binary | std::ios::trunc);
    if (!stream) {
        throw UnpackError("Cannot create file: " + path_utf8(path));
    }
    if (!data.empty()) {
        stream.write(reinterpret_cast<const char*>(data.data()), static_cast<std::streamsize>(data.size()));
    }
    stream.flush();
    if (!stream) {
        throw UnpackError("Failed writing file: " + path_utf8(path));
    }
}

void read_exact_at(std::ifstream& stream, std::uint64_t offset, std::uint8_t* output, std::size_t size,
                   const std::string& what) {
    if (offset > static_cast<std::uint64_t>(std::numeric_limits<std::streamoff>::max())) {
        throw UnpackError("File offset exceeds supported range while reading " + what);
    }
    stream.clear();
    stream.seekg(static_cast<std::streamoff>(offset), std::ios::beg);
    if (!stream) {
        throw UnpackError("Cannot seek to " + what);
    }
    if (size != 0) {
        stream.read(reinterpret_cast<char*>(output), static_cast<std::streamsize>(size));
        if (stream.gcount() != static_cast<std::streamsize>(size)) {
            throw UnpackError("Truncated " + what);
        }
    }
}

// Minimal SHA-256 implementation, used for reproducible client and output fingerprints.
class Sha256 {
public:
    Sha256() : state_{0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
                      0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u} {}

    void update(const std::uint8_t* input, std::size_t size) {
        if (size > (std::numeric_limits<std::uint64_t>::max() - bit_count_) / 8) {
            throw UnpackError("SHA-256 input is too large");
        }
        bit_count_ += static_cast<std::uint64_t>(size) * 8;
        std::size_t offset = 0;
        if (buffer_size_ != 0) {
            const std::size_t take = std::min(size, buffer_.size() - buffer_size_);
            if (take != 0) {
                std::memcpy(buffer_.data() + buffer_size_, input, take);
            }
            buffer_size_ += take;
            offset += take;
            if (buffer_size_ == buffer_.size()) {
                transform(buffer_.data());
                buffer_size_ = 0;
            }
        }
        while (size - offset >= buffer_.size()) {
            transform(input + offset);
            offset += buffer_.size();
        }
        if (offset < size) {
            buffer_size_ = size - offset;
            std::memcpy(buffer_.data(), input + offset, buffer_size_);
        }
    }

    std::array<std::uint8_t, 32> finish() {
        const std::uint64_t original_bits = bit_count_;
        buffer_[buffer_size_++] = 0x80;
        if (buffer_size_ > 56) {
            std::fill(buffer_.begin() + static_cast<std::ptrdiff_t>(buffer_size_), buffer_.end(), 0);
            transform(buffer_.data());
            buffer_size_ = 0;
        }
        std::fill(buffer_.begin() + static_cast<std::ptrdiff_t>(buffer_size_), buffer_.begin() + 56, 0);
        for (unsigned i = 0; i < 8; ++i) {
            buffer_[63 - i] = static_cast<std::uint8_t>(original_bits >> (8 * i));
        }
        transform(buffer_.data());
        std::array<std::uint8_t, 32> digest{};
        for (std::size_t i = 0; i < state_.size(); ++i) {
            digest[i * 4] = static_cast<std::uint8_t>(state_[i] >> 24);
            digest[i * 4 + 1] = static_cast<std::uint8_t>(state_[i] >> 16);
            digest[i * 4 + 2] = static_cast<std::uint8_t>(state_[i] >> 8);
            digest[i * 4 + 3] = static_cast<std::uint8_t>(state_[i]);
        }
        return digest;
    }

private:
    static std::uint32_t rotr(std::uint32_t x, unsigned n) {
        return (x >> n) | (x << (32 - n));
    }

    void transform(const std::uint8_t* block) {
        static constexpr std::array<std::uint32_t, 64> k{
            0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u,
            0x3956c25bu, 0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u,
            0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u,
            0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u,
            0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu,
            0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
            0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u,
            0xc6e00bf3u, 0xd5a79147u, 0x06ca6351u, 0x14292967u,
            0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u,
            0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
            0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u,
            0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
            0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u,
            0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu, 0x682e6ff3u,
            0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u,
            0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u};
        std::array<std::uint32_t, 64> w{};
        for (unsigned i = 0; i < 16; ++i) {
            const std::size_t j = i * 4;
            w[i] = (static_cast<std::uint32_t>(block[j]) << 24) |
                   (static_cast<std::uint32_t>(block[j + 1]) << 16) |
                   (static_cast<std::uint32_t>(block[j + 2]) << 8) |
                   static_cast<std::uint32_t>(block[j + 3]);
        }
        for (unsigned i = 16; i < 64; ++i) {
            const std::uint32_t s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3);
            const std::uint32_t s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16] + s0 + w[i - 7] + s1;
        }
        std::uint32_t a = state_[0], b = state_[1], c = state_[2], d = state_[3];
        std::uint32_t e = state_[4], f = state_[5], g = state_[6], h = state_[7];
        for (unsigned i = 0; i < 64; ++i) {
            const std::uint32_t s1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
            const std::uint32_t choice = (e & f) ^ (~e & g);
            const std::uint32_t temp1 = h + s1 + choice + k[i] + w[i];
            const std::uint32_t s0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
            const std::uint32_t majority = (a & b) ^ (a & c) ^ (b & c);
            const std::uint32_t temp2 = s0 + majority;
            h = g; g = f; f = e; e = d + temp1;
            d = c; c = b; b = a; a = temp1 + temp2;
        }
        state_[0] += a; state_[1] += b; state_[2] += c; state_[3] += d;
        state_[4] += e; state_[5] += f; state_[6] += g; state_[7] += h;
    }

    std::array<std::uint32_t, 8> state_{};
    std::array<std::uint8_t, 64> buffer_{};
    std::size_t buffer_size_ = 0;
    std::uint64_t bit_count_ = 0;
};

std::string sha256_hex(const std::uint8_t* data, std::size_t size) {
    Sha256 hasher;
    hasher.update(data, size);
    const auto digest = hasher.finish();
    return hex_bytes(digest.data(), digest.size());
}

std::string sha256_hex(const Bytes& data) {
    return sha256_hex(data.data(), data.size());
}

// Standard reflected CRC-32 (polynomial 0xEDB88320), used for normalized virtual names.
std::uint32_t crc32(const std::uint8_t* data, std::size_t size) {
    std::uint32_t crc = 0xFFFFFFFFu;
    for (std::size_t i = 0; i < size; ++i) {
        crc ^= data[i];
        for (unsigned bit = 0; bit < 8; ++bit) {
            crc = (crc >> 1) ^ ((crc & 1u) ? 0xEDB88320u : 0u);
        }
    }
    return crc ^ 0xFFFFFFFFu;
}

std::uint32_t crc32(std::string_view data) {
    return crc32(reinterpret_cast<const std::uint8_t*>(data.data()), data.size());
}

std::uint32_t rotl32(std::uint32_t value, unsigned count) {
    return (value << count) | (value >> (32 - count));
}

std::uint32_t xxh32(const std::uint8_t* input, std::size_t length, std::uint32_t seed) {
    static const std::uint8_t empty_input = 0;
    if (input == nullptr) input = &empty_input;
    constexpr std::uint32_t p1 = 0x9E3779B1u;
    constexpr std::uint32_t p2 = 0x85EBCA77u;
    constexpr std::uint32_t p3 = 0xC2B2AE3Du;
    constexpr std::uint32_t p4 = 0x27D4EB2Fu;
    constexpr std::uint32_t p5 = 0x165667B1u;
    const std::uint8_t* p = input;
    const std::uint8_t* const end = input + length;
    std::uint32_t hash;
    if (length >= 16) {
        std::uint32_t v1 = seed + p1 + p2;
        std::uint32_t v2 = seed + p2;
        std::uint32_t v3 = seed;
        std::uint32_t v4 = seed - p1;
        const std::uint8_t* const limit = end - 16;
        do {
            v1 = rotl32(v1 + read_u32_ptr(p) * p2, 13) * p1; p += 4;
            v2 = rotl32(v2 + read_u32_ptr(p) * p2, 13) * p1; p += 4;
            v3 = rotl32(v3 + read_u32_ptr(p) * p2, 13) * p1; p += 4;
            v4 = rotl32(v4 + read_u32_ptr(p) * p2, 13) * p1; p += 4;
        } while (p <= limit);
        hash = rotl32(v1, 1) + rotl32(v2, 7) + rotl32(v3, 12) + rotl32(v4, 18);
    } else {
        hash = seed + p5;
    }
    hash += static_cast<std::uint32_t>(length);
    while (p + 4 <= end) {
        hash = rotl32(hash + read_u32_ptr(p) * p3, 17) * p4;
        p += 4;
    }
    while (p < end) {
        hash = rotl32(hash + static_cast<std::uint32_t>(*p) * p5, 11) * p1;
        ++p;
    }
    hash ^= hash >> 15;
    hash *= p2;
    hash ^= hash >> 13;
    hash *= p3;
    hash ^= hash >> 16;
    return hash;
}

std::uint32_t xtea_mix(std::uint32_t value) {
    return (((value << 4) ^ (value >> 5)) + value);
}

std::array<std::uint32_t, 4> xtea_key_words(const std::array<std::uint8_t, 16>& key) {
    std::array<std::uint32_t, 4> words{};
    for (std::size_t i = 0; i < words.size(); ++i) {
        const std::size_t offset = i * 4;
        words[i] = static_cast<std::uint32_t>(key[offset]) |
                   (static_cast<std::uint32_t>(key[offset + 1]) << 8) |
                   (static_cast<std::uint32_t>(key[offset + 2]) << 16) |
                   (static_cast<std::uint32_t>(key[offset + 3]) << 24);
    }
    return words;
}

Bytes decrypt_xtea4(const Bytes& encrypted, const std::array<std::uint8_t, 16>& key) {
    if (encrypted.size() % 8 != 0) {
        throw UnpackError("XTEA-4 input is not aligned to 8-byte blocks");
    }
    const auto words = xtea_key_words(key);
    std::array<std::pair<std::uint32_t, std::uint32_t>, 4> schedule{};
    std::uint32_t sum = kXteaDelta * 4u;
    for (auto& round : schedule) {
        const std::uint32_t right = sum + words[(sum >> 11) & 3u];
        sum -= kXteaDelta;
        const std::uint32_t left = sum + words[sum & 3u];
        round = {right, left};
    }
    Bytes output(encrypted.size());
    for (std::size_t offset = 0; offset < encrypted.size(); offset += 8) {
        std::uint32_t v0 = read_u32_ptr(encrypted.data() + offset);
        std::uint32_t v1 = read_u32_ptr(encrypted.data() + offset + 4);
        for (const auto& round : schedule) {
            v1 -= xtea_mix(v0) ^ round.first;
            v0 -= xtea_mix(v1) ^ round.second;
        }
        write_u32(output, offset, v0);
        write_u32(output, offset + 4, v1);
    }
    return output;
}

Bytes encrypt_xtea4_for_test(const Bytes& plain, const std::array<std::uint8_t, 16>& key) {
    if (plain.size() % 8 != 0) {
        throw UnpackError("Internal self-test plaintext alignment error");
    }
    const auto words = xtea_key_words(key);
    Bytes output(plain.size());
    for (std::size_t offset = 0; offset < plain.size(); offset += 8) {
        std::uint32_t v0 = read_u32_ptr(plain.data() + offset);
        std::uint32_t v1 = read_u32_ptr(plain.data() + offset + 4);
        std::uint32_t sum = 0;
        for (unsigned round = 0; round < 4; ++round) {
            v0 += xtea_mix(v1) ^ (sum + words[sum & 3u]);
            sum += kXteaDelta;
            v1 += xtea_mix(v0) ^ (sum + words[(sum >> 11) & 3u]);
        }
        write_u32(output, offset, v0);
        write_u32(output, offset + 4, v1);
    }
    return output;
}

Bytes lz4_decompress_block(const std::uint8_t* input, std::size_t input_size, std::size_t expected_size) {
    Bytes output;
    output.reserve(expected_size);
    std::size_t ip = 0;
    while (ip < input_size) {
        const std::uint8_t token = input[ip++];
        std::size_t literal_length = token >> 4;
        if (literal_length == 15) {
            std::uint8_t extension = 255;
            while (extension == 255) {
                if (ip >= input_size) {
                    throw UnpackError("LZ4 failure: truncated literal length");
                }
                extension = input[ip++];
                if (literal_length > std::numeric_limits<std::size_t>::max() - extension) {
                    throw UnpackError("LZ4 failure: literal length overflow");
                }
                literal_length += extension;
            }
        }
        if (literal_length > input_size - ip || literal_length > expected_size - output.size()) {
            throw UnpackError("LZ4 failure: literal bytes exceed input or expected output size");
        }
        output.insert(output.end(), input + ip, input + ip + literal_length);
        ip += literal_length;
        if (ip == input_size) {
            break;
        }
        if (input_size - ip < 2) {
            throw UnpackError("LZ4 failure: truncated match offset");
        }
        const std::size_t match_offset = static_cast<std::size_t>(input[ip]) |
                                         (static_cast<std::size_t>(input[ip + 1]) << 8);
        ip += 2;
        if (match_offset == 0 || match_offset > output.size()) {
            throw UnpackError("LZ4 failure: invalid back-reference");
        }
        std::size_t match_length = static_cast<std::size_t>(token & 0x0Fu) + 4;
        if ((token & 0x0Fu) == 15) {
            std::uint8_t extension = 255;
            while (extension == 255) {
                if (ip >= input_size) {
                    throw UnpackError("LZ4 failure: truncated match length");
                }
                extension = input[ip++];
                if (match_length > std::numeric_limits<std::size_t>::max() - extension) {
                    throw UnpackError("LZ4 failure: match length overflow");
                }
                match_length += extension;
            }
        }
        if (match_length > expected_size - output.size()) {
            throw UnpackError("LZ4 failure: match exceeds expected output size");
        }
        for (std::size_t i = 0; i < match_length; ++i) {
            output.push_back(output[output.size() - match_offset]);
        }
    }
    if (ip != input_size || output.size() != expected_size) {
        throw UnpackError("LZ4 failure: decoded size does not match archive header");
    }
    return output;
}

struct Section {
    std::string name;
    std::uint32_t rva = 0;
    std::uint32_t raw_offset = 0;
    std::uint32_t raw_size = 0;
    std::uint32_t characteristics = 0;
};

class PEImage {
public:
    explicit PEImage(const Bytes& data) : data_(data) {
        try {
            if (data_.size() < 0x40 || data_[0] != 'M' || data_[1] != 'Z') {
                throw UnpackError("Invalid client executable: missing MZ signature");
            }
            const std::uint32_t pe_offset = read_u32(data_, 0x3C);
            if (pe_offset > data_.size() || data_.size() - pe_offset < 24 ||
                data_[pe_offset] != 'P' || data_[pe_offset + 1] != 'E' ||
                data_[pe_offset + 2] != 0 || data_[pe_offset + 3] != 0) {
                throw UnpackError("Invalid client executable: missing or truncated PE signature");
            }
            const std::size_t coff = static_cast<std::size_t>(pe_offset) + 4;
            const std::uint16_t machine = read_u16(data_, coff);
            const std::uint16_t section_count = read_u16(data_, coff + 2);
            const std::uint16_t optional_size = read_u16(data_, coff + 16);
            const std::size_t optional = coff + 20;
            if (machine != 0x8664 || optional_size < 32 || optional > data_.size() ||
                optional_size > data_.size() - optional || read_u16(data_, optional) != 0x20B) {
                throw UnpackError("Invalid client executable: expected an x64 PE32+ image");
            }
            if (section_count == 0 || section_count > 96) {
                throw UnpackError("Invalid client executable: invalid PE section count");
            }
            (void)read_u64(data_, optional + 24); // Bounds-check and parse the PE32+ image base.
            const std::size_t section_table = optional + optional_size;
            if (section_table > data_.size() ||
                static_cast<std::size_t>(section_count) > (data_.size() - section_table) / 40) {
                throw UnpackError("Invalid client executable: truncated section table");
            }
            sections_.reserve(section_count);
            for (std::size_t i = 0; i < section_count; ++i) {
                const std::size_t off = section_table + i * 40;
                Section section;
                for (std::size_t j = 0; j < 8 && data_[off + j] != 0; ++j) {
                    section.name.push_back(static_cast<char>(data_[off + j]));
                }
                section.rva = read_u32(data_, off + 12);
                section.raw_size = read_u32(data_, off + 16);
                section.raw_offset = read_u32(data_, off + 20);
                section.characteristics = read_u32(data_, off + 36);
                if (section.raw_offset > data_.size() || section.raw_size > data_.size() - section.raw_offset) {
                    throw UnpackError("Invalid client executable: truncated PE section data");
                }
                sections_.push_back(std::move(section));
            }
        } catch (const UnpackError&) {
            throw;
        } catch (const std::exception& error) {
            throw UnpackError(std::string("Invalid client executable: ") + error.what());
        }
    }

    std::size_t rva_to_offset(std::uint32_t rva, std::size_t length) const {
        const std::uint64_t start = rva;
        const std::uint64_t end = start + length;
        for (const auto& section : sections_) {
            const std::uint64_t section_start = section.rva;
            const std::uint64_t section_end = section_start + section.raw_size;
            if (start >= section_start && end <= section_end) {
                const std::uint64_t offset = static_cast<std::uint64_t>(section.raw_offset) + (start - section_start);
                if (offset > data_.size() || length > data_.size() - static_cast<std::size_t>(offset)) {
                    break;
                }
                return static_cast<std::size_t>(offset);
            }
        }
        throw UnpackError("RVA " + hex_u32(rva) + " is not backed by file data");
    }

    const std::vector<Section>& sections() const { return sections_; }

private:
    const Bytes& data_;
    std::vector<Section> sections_;
};

struct KeyInfo {
    std::array<std::uint8_t, 16> key{};
    std::array<std::uint32_t, 4> words{};
    std::uint32_t key_rva = 0;
    std::uint64_t key_file_offset = 0;
    std::uint32_t loop_rva = 0;
    std::string client_sha256;
};

bool key_signature_matches(const Bytes& data, std::size_t offset) {
    static constexpr std::array<std::uint8_t, 52> pattern{
        0x8b, 0x1e, 0x8b, 0xcb, 0xc1, 0xe9, 0x05, 0x8b, 0xc3, 0x44, 0x8b, 0x1d,
        0, 0, 0, 0, 0x8b, 0x7e, 0x04, 0x48, 0x8d, 0x76, 0x08, 0x44, 0x8b, 0x15,
        0, 0, 0, 0, 0x4c, 0x8b, 0x05, 0, 0, 0, 0, 0x8b, 0x15, 0, 0, 0, 0,
        0xc1, 0xe0, 0x04, 0x81, 0xc2, 0x72, 0xf3, 0x6e, 0x3c};
    static constexpr std::array<std::pair<std::size_t, std::size_t>, 4> wildcards{{
        {12, 16}, {26, 30}, {33, 37}, {39, 43}}};
    if (offset > data.size() || data.size() - offset < pattern.size()) {
        return false;
    }
    for (std::size_t i = 0; i < pattern.size(); ++i) {
        bool wildcard = false;
        for (const auto& range : wildcards) {
            if (i >= range.first && i < range.second) {
                wildcard = true;
                break;
            }
        }
        if (!wildcard && data[offset + i] != pattern[i]) {
            return false;
        }
    }
    return true;
}

std::int64_t signed_rel32(const Bytes& data, std::size_t offset) {
    const std::uint32_t raw = read_u32(data, offset);
    if ((raw & 0x80000000u) != 0) {
        return static_cast<std::int64_t>(raw) - 0x100000000ll;
    }
    return static_cast<std::int64_t>(raw);
}

KeyInfo discover_key(const Bytes& client) {
    const PEImage pe(client);
    std::vector<KeyInfo> found;
    static constexpr std::array<std::size_t, 4> disp_offsets{12, 26, 33, 39};
    static constexpr std::array<std::size_t, 4> instruction_ends{16, 30, 37, 43};
    for (const auto& section : pe.sections()) {
        if ((section.characteristics & 0x20000000u) == 0 || section.raw_size < 52) {
            continue;
        }
        const std::size_t raw = section.raw_offset;
        const std::size_t scan_size = section.raw_size;
        for (std::size_t i = 0; i <= scan_size - 52; ++i) {
            const std::size_t match_offset = raw + i;
            if (!key_signature_matches(client, match_offset)) {
                continue;
            }
            const std::uint64_t loop_rva64 = static_cast<std::uint64_t>(section.rva) + i;
            if (loop_rva64 > std::numeric_limits<std::uint32_t>::max()) {
                continue;
            }
            std::array<std::uint32_t, 4> refs{};
            bool valid = true;
            for (std::size_t j = 0; j < refs.size(); ++j) {
                const std::int64_t instruction_end = static_cast<std::int64_t>(loop_rva64) +
                                                     static_cast<std::int64_t>(instruction_ends[j]);
                const std::int64_t target = instruction_end + signed_rel32(client, match_offset + disp_offsets[j]);
                if (target < 0 || target > std::numeric_limits<std::uint32_t>::max()) {
                    valid = false;
                    break;
                }
                refs[j] = static_cast<std::uint32_t>(target);
            }
            if (!valid || static_cast<std::uint64_t>(refs[1]) != static_cast<std::uint64_t>(refs[0]) + 12u ||
                static_cast<std::uint64_t>(refs[2]) != static_cast<std::uint64_t>(refs[0]) + 4u ||
                static_cast<std::uint64_t>(refs[3]) != static_cast<std::uint64_t>(refs[0]) + 8u) {
                continue;
            }
            std::size_t key_offset = 0;
            try {
                key_offset = pe.rva_to_offset(refs[0], 16);
            } catch (const UnpackError&) {
                continue;
            }
            KeyInfo info;
            std::copy_n(client.data() + key_offset, info.key.size(), info.key.begin());
            info.words = xtea_key_words(info.key);
            info.key_rva = refs[0];
            info.key_file_offset = key_offset;
            info.loop_rva = static_cast<std::uint32_t>(loop_rva64);
            found.push_back(info);
        }
    }
    if (found.size() != 1) {
        throw UnpackError("Expected one supported XTEA-4 routine, found " + std::to_string(found.size()) +
                          ". This client build is unsupported; no file-offset guessing was attempted.");
    }
    found.front().client_sha256 = sha256_hex(client);
    return found.front();
}

struct Entry {
    std::size_t index = 0;
    std::uint64_t header_offset = 0;
    std::uint32_t original_size = 0;
    std::uint32_t stored_size = 0;
    std::uint32_t checksum = 0;
    std::uint32_t data_offset = 0;
    std::uint32_t compressed_size = 0;
    std::uint32_t name_hash = 0;
};

std::vector<Entry> read_index(const fs::path& archive, std::uint64_t max_file_size,
                              std::uint64_t max_total_size) {
    if (max_file_size == 0 || max_total_size == 0) {
        throw UnpackError("Size limits must be positive");
    }
    std::error_code ec;
    const std::uint64_t file_size = fs::file_size(archive, ec);
    if (ec) {
        throw UnpackError("Cannot read archive size for " + path_utf8(archive) + ": " + ec.message());
    }
    if (file_size < 4) {
        throw UnpackError("Not an ALT2 archive: truncated magic");
    }
    std::ifstream stream(archive, std::ios::binary);
    if (!stream) {
        throw UnpackError("Cannot open archive: " + path_utf8(archive));
    }
    std::array<std::uint8_t, 4> magic_bytes{};
    read_exact_at(stream, 0, magic_bytes.data(), magic_bytes.size(), "archive magic");
    if (read_u32_ptr(magic_bytes.data()) != kMagic) {
        throw UnpackError("Not an ALT2 archive: expected magic 0x000fed0c");
    }
    std::vector<Entry> entries;
    std::uint64_t total_size = 0;
    std::uint64_t position = 4;
    while (position < file_size) {
        if (file_size - position < kHeaderSize) {
            std::ostringstream message;
            message << "Truncated header at 0x" << std::hex << position;
            throw UnpackError(message.str());
        }
        std::array<std::uint8_t, kHeaderSize> header{};
        read_exact_at(stream, position, header.data(), header.size(), "entry header");
        Entry entry;
        entry.index = entries.size();
        entry.header_offset = position;
        entry.original_size = read_u32_ptr(header.data());
        entry.stored_size = read_u32_ptr(header.data() + 4);
        entry.checksum = read_u32_ptr(header.data() + 8);
        entry.data_offset = read_u32_ptr(header.data() + 12);
        entry.compressed_size = read_u32_ptr(header.data() + 16);
        entry.name_hash = read_u32_ptr(header.data() + 20);
        if (entry.data_offset != position + kHeaderSize) {
            throw UnpackError("Invalid payload offset at entry " + std::to_string(entry.index));
        }
        const std::uint64_t expected_stored = (static_cast<std::uint64_t>(entry.compressed_size) + 7u) & ~7ull;
        if (entry.stored_size != expected_stored) {
            throw UnpackError("Invalid encrypted block size at entry " + std::to_string(entry.index));
        }
        const std::uint64_t end = static_cast<std::uint64_t>(entry.data_offset) + entry.stored_size;
        if (end > file_size) {
            throw UnpackError("Truncated payload at entry " + std::to_string(entry.index));
        }
        if (entry.original_size > max_file_size || entry.stored_size > max_file_size ||
            entry.original_size > max_total_size || total_size > max_total_size - entry.original_size) {
            throw UnpackError("Size safety limit exceeded at entry " + std::to_string(entry.index));
        }
        total_size += entry.original_size;
        if (entry.compressed_size == 0 && entry.original_size != 0) {
            throw UnpackError("Empty payload for nonempty entry " + std::to_string(entry.index));
        }
        entries.push_back(entry);
        if (entries.size() > kMaxEntries) {
            throw UnpackError("Too many archive entries");
        }
        position = end;
    }
    return entries;
}

Bytes decode_entry(std::ifstream& stream, const Entry& entry, const std::array<std::uint8_t, 16>& key) {
    Bytes encrypted(entry.stored_size);
    read_exact_at(stream, entry.data_offset, encrypted.data(), encrypted.size(),
                  "payload at entry " + std::to_string(entry.index));
    Bytes decrypted = decrypt_xtea4(encrypted, key);
    if (entry.compressed_size > decrypted.size()) {
        throw UnpackError("Compressed size exceeds decrypted payload at entry " + std::to_string(entry.index));
    }
    Bytes payload;
    if (entry.compressed_size == entry.original_size) {
        payload.assign(decrypted.begin(), decrypted.begin() + entry.compressed_size);
    } else {
        try {
            payload = lz4_decompress_block(decrypted.data(), entry.compressed_size, entry.original_size);
        } catch (const UnpackError& error) {
            throw UnpackError("LZ4 failure at entry " + std::to_string(entry.index) +
                              ": wrong key or damaged archive (" + error.what() + ")");
        }
    }
    if (payload.size() != entry.original_size) {
        throw UnpackError("Size mismatch at entry " + std::to_string(entry.index));
    }
    const std::uint32_t checksum = xxh32(payload.data(), payload.size(), kMagic);
    if (checksum != entry.checksum) {
        throw UnpackError("XXH32 mismatch at entry " + std::to_string(entry.index) +
                          ": wrong key or damaged archive");
    }
    return payload;
}

std::string normalize_name(std::string name) {
    for (char& c : name) {
        if (c == '\\') {
            c = '/';
        } else if (c >= 'A' && c <= 'Z') {
            c = static_cast<char>(c - 'A' + 'a');
        }
    }
    return name;
}

std::uint32_t name_hash(std::string_view name) {
    const std::string normalized = normalize_name(std::string(name));
    return crc32(normalized);
}

bool ascii_alpha(unsigned char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}

bool ascii_digit(unsigned char c) {
    return c >= '0' && c <= '9';
}

bool ascii_word(unsigned char c) {
    return ascii_alpha(c) || ascii_digit(c) || c == '_';
}

std::string safe_relative_name(std::string name) {
    name = normalize_name(std::move(name));
    if (name.empty() || name.size() > 1024) {
        throw UnpackError("Unsafe archive filename: empty or too long");
    }
    if (name.size() >= 3 && ascii_alpha(static_cast<unsigned char>(name[0])) &&
        name[1] == ':' && name[2] == '/') {
        name = std::string("_drives/") + name[0] + "/" + name.substr(3);
    }
    std::size_t start = 0;
    static const std::set<std::string> reserved{"con", "prn", "aux", "nul", "com1", "com2", "com3", "com4",
                                                 "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2",
                                                 "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"};
    while (start <= name.size()) {
        const std::size_t slash = name.find('/', start);
        const std::size_t end = slash == std::string::npos ? name.size() : slash;
        const std::string component = name.substr(start, end - start);
        if (component.empty() || component == "." || component == ".." || component.size() > 240 ||
            component.back() == ' ' || component.back() == '.') {
            throw UnpackError("Unsafe archive filename: " + name);
        }
        for (unsigned char c : component) {
            if (c < 0x20 || c == 0x7f || c == '<' || c == '>' || c == ':' || c == '"' || c == '|' ||
                c == '?' || c == '*') {
                throw UnpackError("Unsafe archive filename: " + name);
            }
        }
        std::string stem = component.substr(0, component.find('.'));
        for (char& c : stem) {
            if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
        }
        if (reserved.count(stem) != 0) {
            throw UnpackError("Unsafe archive filename: " + name);
        }
        if (slash == std::string::npos) {
            break;
        }
        start = slash + 1;
    }
    return name;
}

bool path_char(unsigned char c) {
    return ascii_alpha(c) || ascii_digit(c) || c == '_' || c == '.' || c == '/' || c == ':' ||
           c == '\\' || c == ' ' || c == '-';
}

bool is_separator(unsigned char c) {
    return c == '/' || c == '\\' || c == ' ';
}

bool has_suffix_ci(std::string_view text, std::size_t end, std::string_view suffix) {
    if (end < suffix.size()) return false;
    const std::size_t start = end - suffix.size();
    for (std::size_t i = 0; i < suffix.size(); ++i) {
        unsigned char a = static_cast<unsigned char>(text[start + i]);
        unsigned char b = static_cast<unsigned char>(suffix[i]);
        if (a >= 'A' && a <= 'Z') a = static_cast<unsigned char>(a - 'A' + 'a');
        if (b >= 'A' && b <= 'Z') b = static_cast<unsigned char>(b - 'A' + 'a');
        if (a != b) return false;
    }
    return true;
}

bool contains_ci(std::string_view haystack, std::string_view needle) {
    if (needle.empty()) return true;
    if (haystack.size() < needle.size()) return false;
    const auto equal_ci = [](char a, char b) {
        unsigned char x = static_cast<unsigned char>(a);
        unsigned char y = static_cast<unsigned char>(b);
        if (x >= 'A' && x <= 'Z') x = static_cast<unsigned char>(x - 'A' + 'a');
        if (y >= 'A' && y <= 'Z') y = static_cast<unsigned char>(y - 'A' + 'a');
        return x == y;
    };
    for (std::size_t i = 0; i + needle.size() <= haystack.size(); ++i) {
        if (std::equal(needle.begin(), needle.end(), haystack.begin() + static_cast<std::ptrdiff_t>(i), equal_ci)) {
            return true;
        }
    }
    return false;
}

// Best-effort content label for payloads whose original name stays unknown.
// This only chooses an honest extension for unnamed files; it never claims a
// name. Unrecognized content stays "bin".
std::string detect_content_type(const Bytes& data) {
    const std::size_t size = data.size();
    if (size == 0) return "empty";
    if (size >= 8 && std::memcmp(data.data(), "\x89PNG\r\n\x1a\n", 8) == 0) return "png";
    if (size >= 4 && std::memcmp(data.data(), "DDS ", 4) == 0) return "dds";
    if (size >= 3 && data[0] == 0xFF && data[1] == 0xD8 && data[2] == 0xFF) return "jpg";
    if (size >= 12 && std::memcmp(data.data(), "RIFF", 4) == 0) {
        if (std::memcmp(data.data() + 8, "AVI ", 4) == 0) return "avi";
        if (std::memcmp(data.data() + 8, "WAVE", 4) == 0) return "wav";
        return "riff";
    }
    if (size >= 4 && std::memcmp(data.data(), "OggS", 4) == 0) return "ogg";
    if (size >= 6 && std::memcmp(data.data(), "Granny", 6) == 0) return "gr2";
    if (size >= 4 && (std::memcmp(data.data(), "\x00\x01\x00\x00", 4) == 0 ||
                      std::memcmp(data.data(), "OTTO", 4) == 0 ||
                      std::memcmp(data.data(), "true", 4) == 0 ||
                      std::memcmp(data.data(), "ttcf", 4) == 0)) {
        return "ttf";
    }
    if (size >= 2 && data[0] == 'B' && data[1] == 'M') return "bmp";
    if (size >= 18 && std::memcmp(data.data() + size - 18, "TRUEVISION-XFILE.\x00", 18) == 0) {
        return "tga";
    }
    if (size >= 18) {
        const unsigned colormap_type = data[1];
        const unsigned image_type = data[2];
        const unsigned width = static_cast<unsigned>(data[12]) | (static_cast<unsigned>(data[13]) << 8);
        const unsigned height = static_cast<unsigned>(data[14]) | (static_cast<unsigned>(data[15]) << 8);
        const unsigned bits_per_pixel = data[16];
        const bool header_ok =
            (colormap_type == 0 || colormap_type == 1) &&
            (image_type == 0 || image_type == 1 || image_type == 2 || image_type == 3 ||
             image_type == 9 || image_type == 10 || image_type == 11) &&
            width >= 1 && width <= 16384 && height >= 1 && height <= 16384 &&
            (bits_per_pixel == 8 || bits_per_pixel == 15 || bits_per_pixel == 16 ||
             bits_per_pixel == 24 || bits_per_pixel == 32) &&
            (data[0] == 0 || data[0] == 1 || data[0] == 2 || data[0] == 3 ||
             data[0] == 10 || data[0] == 11);
        if (header_ok) return "tga";
    }
    const std::size_t head_size = std::min<std::size_t>(size, 4096);
    const std::string_view head(reinterpret_cast<const char*>(data.data()), head_size);
    std::size_t control = 0;
    bool has_nul = false;
    for (unsigned char c : head) {
        if (c == 0) { has_nul = true; break; }
        if (c < 0x20 && c != 9 && c != 10 && c != 13 && c != 12 && c != 27) ++control;
    }
    if (!has_nul && control <= 8) {
        if (head_size >= 5 && head.substr(0, 5) == "<?xml") return "xml";
        if (contains_ci(head, "<xml")) return "xml";
        if (contains_ci(head, "racedatascript")) {
            if (contains_ci(head, "motionfilename") || contains_ci(head, "submotion") ||
                contains_ci(head, "nodeevent")) {
                return "msa";
            }
            return "msm";
        }
        static constexpr std::array<std::string_view, 5> strong_markers{{
            "import ", "from ", "def ", "class ", "self."}};
        static constexpr std::array<std::string_view, 4> weak_markers{{
            "__init__", "elif ", "except", "lambda"}};
        std::size_t strong = 0;
        std::size_t weak = 0;
        for (const auto marker : strong_markers) {
            if (contains_ci(head, marker)) ++strong;
        }
        for (const auto marker : weak_markers) {
            if (contains_ci(head, marker)) ++weak;
        }
        if (strong != 0 || strong + weak >= 2) return "py";
        std::size_t line_begin = 0;
        for (unsigned line_index = 0; line_index < 40 && line_begin <= head.size(); ++line_index) {
            const std::size_t line_end = head.find('\n', line_begin);
            const std::size_t stop = line_end == std::string_view::npos ? head.size() : line_end;
            std::string_view line = head.substr(line_begin, stop - line_begin);
            while (!line.empty() && (line.front() == ' ' || line.front() == '\t' ||
                                     line.front() == '\r')) line.remove_prefix(1);
            while (!line.empty() && (line.back() == ' ' || line.back() == '\t' ||
                                     line.back() == '\r')) line.remove_suffix(1);
            const std::size_t equals = line.find('=');
            if (!line.empty() && equals != std::string_view::npos && line.front() != '#') {
                std::string_view left = line.substr(0, equals);
                while (!left.empty() && (left.back() == ' ' || left.back() == '\t')) left.remove_suffix(1);
                // Match Python's str.isupper(): at least one cased character,
                // all cased characters uppercase; spaces disqualify.
                bool has_upper = false;
                bool is_upper = !left.empty();
                for (unsigned char c : left) {
                    if (c == ' ' || (c >= 'a' && c <= 'z')) { is_upper = false; break; }
                    if (c >= 'A' && c <= 'Z') has_upper = true;
                }
                if (is_upper && has_upper) return "py";
            }
            if (line_end == std::string_view::npos) break;
            line_begin = line_end + 1;
        }
        return "txt";
    }
    return "bin";
}

std::string type_extension(const std::string& detected) {
    if (detected == "png") return "png";
    if (detected == "jpg") return "jpg";
    if (detected == "dds") return "dds";
    if (detected == "avi") return "avi";
    if (detected == "wav") return "wav";
    if (detected == "ogg") return "ogg";
    if (detected == "gr2") return "gr2";
    if (detected == "ttf") return "ttf";
    if (detected == "bmp") return "bmp";
    if (detected == "tga") return "tga";
    if (detected == "xml") return "xml";
    if (detected == "msm") return "msm";
    if (detected == "msa") return "msa";
    if (detected == "py") return "py";
    if (detected == "txt") return "txt";
    return "bin";
}

class NameResolver {
public:
    explicit NameResolver(const std::vector<Entry>& entries) {
        for (const auto& entry : entries) hashes_.insert(entry.name_hash);
    }

    explicit NameResolver(const std::set<std::uint32_t>& hashes) : hashes_(hashes) {}

    void add_hash_for_test(std::uint32_t hash) { hashes_.insert(hash); }

    void add(std::string name) {
        name = normalize_name(std::move(name));
        if (hashes_.find(name_hash(name)) == hashes_.end()) {
            return;
        }
        try {
            (void)safe_relative_name(name);
        } catch (const UnpackError&) {
            return;
        }
        matches_[name_hash(name)].insert(std::move(name));
    }

    void load(const fs::path& path) {
        Bytes bytes = read_file(path);
        std::string contents(bytes.begin(), bytes.end());
        std::size_t line_number = 0;
        std::size_t begin = 0;
        while (begin <= contents.size()) {
            const std::size_t end = contents.find('\n', begin);
            std::string line = contents.substr(begin, end == std::string::npos ? std::string::npos : end - begin);
            if (!line.empty() && line.back() == '\r') line.pop_back();
            if (line_number == 0 && line.size() >= 3 &&
                static_cast<unsigned char>(line[0]) == 0xEF &&
                static_cast<unsigned char>(line[1]) == 0xBB &&
                static_cast<unsigned char>(line[2]) == 0xBF) {
                line.erase(0, 3);
            }
            const std::string trimmed = trim_ascii(line);
            if (!trimmed.empty() && trimmed[0] != '#') {
                add(trimmed);
            }
            ++line_number;
            if (end == std::string::npos) break;
            begin = end + 1;
        }
    }

    void scan(const Bytes& data) {
        if (data.empty()) return;
        const std::string_view text(reinterpret_cast<const char*>(data.data()), data.size());
        // Fragments become cross-file combination inputs in generate(); the
        // per-call sets of the original design could only pair within one file.
        std::set<std::string> directories;
        scan_path_references(text);
        scan_imports(text);
        scan_static_assignments(text, directories);
        scan_quoted_directories(text, directories);
        for (const auto& directory : directories) {
            if (directories_.size() >= kDirectoryLimit) break;
            directories_.insert(directory);
        }
        scan_tokens(text);
    }

    // Deterministic last-resort candidates, still CRC32-checked by add().
    // The client stores only CRC32(name), so unreferenced names can only be
    // found by combining observed directories, bare basenames, identifier
    // tokens, and exhaustive very short stems. Caps keep the search bounded.
    void generate() {
        std::vector<std::string> directories(directories_.begin(), directories_.end());
        if (directories.size() > kDirectoryLimit) directories.resize(kDirectoryLimit);
        std::vector<std::string> fragments(bare_fragments_.begin(), bare_fragments_.end());
        if (fragments.size() > kBareFragmentLimit) fragments.resize(kBareFragmentLimit);
        std::uint64_t combinations = 0;
        bool stop = false;
        for (const auto& directory : directories) {
            if (stop) break;
            for (const auto& fragment : fragments) {
                if (combinations >= kDirectoryCombinationLimit) {
                    stop = true;
                    break;
                }
                ++combinations;
                add(directory + fragment);
            }
        }
        std::vector<std::string> stems;
        const std::size_t base = kStemCharacters.size();
        for (unsigned length = 1; length <= 2; ++length) {
            const std::size_t total = length == 1 ? base : base * base;
            for (std::size_t value = 0; value < total; ++value) {
                std::string stem(length, ' ');
                std::size_t rest = value;
                for (unsigned k = length; k-- > 0;) {
                    stem[k] = kStemCharacters[rest % base];
                    rest /= base;
                }
                stems.push_back(std::move(stem));
            }
        }
        for (const auto& stem : stems) {
            for (const auto extension : kAllExtensions) {
                add(stem + std::string(extension));
            }
            const std::size_t directory_limit = std::min(directories.size(), kStemDirectoryLimit);
            for (std::size_t d = 0; d < directory_limit; ++d) {
                for (const auto extension : kStemExtensions) {
                    add(directories[d] + stem + std::string(extension));
                }
            }
        }
        std::vector<std::string> tokens(tokens_.begin(), tokens_.end());
        if (tokens.size() > kTokenLimit) tokens.resize(kTokenLimit);
        for (const auto& token : tokens) {
            for (const auto extension : kTokenExtensions) {
                add(token + std::string(extension));
            }
            add("ui" + token + ".py");
            add("ui" + token + ".pyc");
        }
    }

    std::string resolved(std::uint32_t hash) const {
        const auto found = matches_.find(hash);
        if (found == matches_.end() || found->second.size() != 1) return {};
        return *found->second.begin();
    }

    std::vector<std::string> candidates(std::uint32_t hash) const {
        std::vector<std::string> result;
        const auto found = matches_.find(hash);
        if (found != matches_.end()) result.assign(found->second.begin(), found->second.end());
        return result;
    }

private:
    static std::string trim_ascii(std::string_view value) {
        std::size_t begin = 0;
        while (begin < value.size() && (value[begin] == ' ' || value[begin] == '\t' || value[begin] == '\r' || value[begin] == '\n')) ++begin;
        std::size_t end = value.size();
        while (end > begin && (value[end - 1] == ' ' || value[end - 1] == '\t' || value[end - 1] == '\r' || value[end - 1] == '\n')) --end;
        return std::string(value.substr(begin, end - begin));
    }

    static bool identifier(std::string_view value) {
        if (value.empty()) return false;
        std::size_t i = 0;
        if (value.substr(0, 5) == "self.") i = 5;
        if (i >= value.size() || !(ascii_alpha(static_cast<unsigned char>(value[i])) || value[i] == '_')) return false;
        for (++i; i < value.size(); ++i) {
            const unsigned char c = static_cast<unsigned char>(value[i]);
            if (!(ascii_alpha(c) || ascii_digit(c) || c == '_')) return false;
        }
        return true;
    }

    void scan_path_references(std::string_view text) {
        static const std::array<std::string_view, 34> extensions{
            ".pyc", ".pyo", ".py", ".msm", ".msa", ".mse", ".msf", ".txt", ".xml", ".json",
            ".cfg", ".ini", ".sub", ".dds", ".tga", ".png", ".jpg", ".jpeg", ".bmp", ".psd",
            ".gr2", ".wav", ".mp3", ".ogg", ".avi", ".ttf", ".otf", ".def", ".bin", ".dat",
            ".sct", ".atr", ".raw", ".wtr"};
        std::size_t work = 0;
        std::size_t pos = 0;
        while (pos < text.size() && work < 300000) {
            if (!path_char(static_cast<unsigned char>(text[pos]))) {
                ++pos;
                continue;
            }
            const std::size_t run_begin = pos;
            while (pos < text.size() && path_char(static_cast<unsigned char>(text[pos]))) ++pos;
            const std::size_t run_end = pos;
            for (std::size_t dot = run_begin; dot < run_end && work < 300000; ++dot) {
                if (text[dot] != '.') continue;
                for (const std::string_view extension : extensions) {
                    if (dot + extension.size() > run_end || !has_suffix_ci(text, dot + extension.size(), extension)) continue;
                    const std::size_t end = dot + extension.size();
                    if (end < text.size() && ascii_word(static_cast<unsigned char>(text[end]))) continue;
                    const std::size_t earliest = end > 240 ? std::max(run_begin, end - 240) : run_begin;
                    for (std::size_t start = earliest; start < end; ++start) {
                        if (start != run_begin && !is_separator(static_cast<unsigned char>(text[start - 1]))) continue;
                        if (end - start > 240) continue;
                        if (++work > 300000) break;
                        std::string candidate(text.substr(start, end - start));
                        add(candidate);
                        remember_bare(candidate);
                    }
                }
            }
        }
    }

    void remember_bare(const std::string& candidate) {
        if (candidate.find('/') == std::string::npos &&
            candidate.find('\\') == std::string::npos &&
            bare_fragments_.size() < kBareFragmentLimit) {
            bare_fragments_.insert(candidate);
        }
    }

    void scan_tokens(std::string_view text) {
        std::size_t i = 0;
        while (i < text.size() && tokens_.size() < kTokenLimit) {
            const unsigned char c = static_cast<unsigned char>(text[i]);
            if (!(ascii_alpha(c) || c == '_')) {
                ++i;
                continue;
            }
            std::size_t j = i + 1;
            while (j < text.size() && j - i <= 40) {
                const unsigned char w = static_cast<unsigned char>(text[j]);
                if (!(ascii_alpha(w) || ascii_digit(w) || w == '_')) break;
                ++j;
            }
            if (j - i >= 2 && tokens_.size() < kTokenLimit) {
                std::string token(text.substr(i, j - i));
                for (char& ch : token) {
                    if (ch >= 'A' && ch <= 'Z') ch = static_cast<char>(ch - 'A' + 'a');
                }
                tokens_.insert(std::move(token));
            }
            i = j;
        }
    }

    void scan_imports(std::string_view text) {
        std::size_t begin = 0;
        while (begin < text.size()) {
            const std::size_t end = text.find('\n', begin);
            const std::size_t line_end = end == std::string_view::npos ? text.size() : end;
            std::string line = trim_ascii(text.substr(begin, line_end - begin));
            if (line.size() <= 4096) {
                std::string_view remainder;
                bool from_import = false;
                if (line.rfind("from ", 0) == 0 || line.rfind("from\t", 0) == 0) {
                    remainder = std::string_view(line).substr(5);
                    from_import = true;
                } else if (line.rfind("import ", 0) == 0 || line.rfind("import\t", 0) == 0) {
                    remainder = std::string_view(line).substr(7);
                }
                if (!remainder.empty()) {
                    const std::size_t comment = remainder.find('#');
                    if (comment != std::string_view::npos) remainder = remainder.substr(0, comment);
                    if (from_import) {
                        const std::size_t stop = remainder.find_first_of(" \t");
                        add_module(remainder.substr(0, stop));
                    } else {
                        std::size_t item_begin = 0;
                        while (item_begin <= remainder.size()) {
                            const std::size_t comma = remainder.find(',', item_begin);
                            std::string item = trim_ascii(remainder.substr(item_begin,
                                comma == std::string_view::npos ? std::string_view::npos : comma - item_begin));
                            const std::size_t alias = item.find(" as ");
                            if (alias != std::string::npos) item.resize(alias);
                            const std::size_t whitespace = item.find_first_of(" \t");
                            if (whitespace != std::string::npos) item.resize(whitespace);
                            add_module(item);
                            if (comma == std::string_view::npos) break;
                            item_begin = comma + 1;
                        }
                    }
                }
            }
            if (end == std::string_view::npos) break;
            begin = end + 1;
        }
    }

    void add_module(std::string_view module_view) {
        if (module_view.empty() || module_view.size() > 240) return;
        std::string module(module_view);
        if (module.front() == '.' || module.back() == '.') return;
        bool expect_identifier_start = true;
        for (unsigned char c : module) {
            if (c == '.') {
                if (expect_identifier_start) return;
                expect_identifier_start = true;
            } else if (expect_identifier_start) {
                if (!(ascii_alpha(c) || c == '_')) return;
                expect_identifier_start = false;
            } else if (!(ascii_alpha(c) || ascii_digit(c) || c == '_')) {
                return;
            }
        }
        if (expect_identifier_start) return;
        std::replace(module.begin(), module.end(), '.', '/');
        std::string derived = module + ".py";
        add(derived);
        remember_bare(derived);
        derived = module + ".pyc";
        add(derived);
        remember_bare(derived);
        derived = module + "/__init__.py";
        add(derived);
        remember_bare(derived);
    }

    static bool parse_string_expression(std::string_view expression,
                                        const std::map<std::string, std::string>& values,
                                        std::string& result) {
        std::size_t i = 0;
        result.clear();
        bool need_term = true;
        while (true) {
            while (i < expression.size() && (expression[i] == ' ' || expression[i] == '\t' || expression[i] == '\r')) ++i;
            if (i == expression.size()) return !need_term;
            if (!need_term) return false;
            std::string term;
            if (expression[i] == '\'' || expression[i] == '"') {
                const char quote = expression[i++];
                const std::size_t start = i;
                while (i < expression.size() && expression[i] != quote) {
                    if (!path_char(static_cast<unsigned char>(expression[i]))) return false;
                    ++i;
                    if (i - start > 240) return false;
                }
                if (i >= expression.size()) return false;
                term.assign(expression.substr(start, i - start));
                ++i;
            } else {
                const std::size_t start = i;
                while (i < expression.size() &&
                       (ascii_alpha(static_cast<unsigned char>(expression[i])) ||
                        ascii_digit(static_cast<unsigned char>(expression[i])) || expression[i] == '_' || expression[i] == '.')) ++i;
                const std::string key(expression.substr(start, i - start));
                if (!identifier(key)) return false;
                const auto found = values.find(key);
                if (found == values.end()) return false;
                term = found->second;
            }
            if (term.size() > 1024 || result.size() > 1024 - term.size()) return false;
            result += term;
            while (i < expression.size() && (expression[i] == ' ' || expression[i] == '\t' || expression[i] == '\r')) ++i;
            if (i == expression.size()) return true;
            if (expression[i] != '+') return false;
            ++i;
            need_term = true;
        }
    }

    void scan_static_assignments(std::string_view text, std::set<std::string>& directories) {
        std::map<std::string, std::string> values;
        std::size_t begin = 0;
        while (begin < text.size() && values.size() < 2048) {
            const std::size_t end = text.find('\n', begin);
            const std::size_t line_end = end == std::string_view::npos ? text.size() : end;
            const std::string line(text.substr(begin, line_end - begin));
            if (line.size() <= 4096) {
                bool quoted = false;
                char quote = 0;
                std::size_t equal = std::string::npos;
                for (std::size_t i = 0; i < line.size(); ++i) {
                    const char c = line[i];
                    if (quoted) {
                        if (c == quote) quoted = false;
                    } else if (c == '\'' || c == '"') {
                        quoted = true;
                        quote = c;
                    } else if (c == '#') {
                        break;
                    } else if (c == '=') {
                        equal = i;
                        break;
                    }
                }
                if (equal != std::string::npos) {
                    const std::string left = trim_ascii(std::string_view(line).substr(0, equal));
                    if (identifier(left)) {
                        std::string expression = line.substr(equal + 1);
                        bool in_quote = false;
                        char active_quote = 0;
                        for (std::size_t i = 0; i < expression.size(); ++i) {
                            if (in_quote) {
                                if (expression[i] == active_quote) in_quote = false;
                            } else if (expression[i] == '\'' || expression[i] == '"') {
                                in_quote = true;
                                active_quote = expression[i];
                            } else if (expression[i] == '#') {
                                expression.resize(i);
                                break;
                            }
                        }
                        std::string value;
                        if (parse_string_expression(expression, values, value)) {
                            values[left] = value;
                            add(value);
                            if (!value.empty() && (value.back() == '/' || value.back() == '\\') && directories.size() < 128) {
                                directories.insert(value);
                            }
                        }
                    }
                }
            }
            if (end == std::string_view::npos) break;
            begin = end + 1;
        }
    }

    void scan_quoted_directories(std::string_view text, std::set<std::string>& directories) {
        for (std::size_t i = 0; i < text.size() && directories.size() < 128; ++i) {
            if (text[i] != '\'' && text[i] != '"') continue;
            const char quote = text[i];
            const std::size_t start = i + 1;
            std::size_t end = start;
            while (end < text.size() && end - start < 200 && path_char(static_cast<unsigned char>(text[end]))) ++end;
            if (end > start && end < text.size() && text[end] == quote &&
                (text[end - 1] == '/' || text[end - 1] == '\\')) {
                directories.emplace(text.substr(start, end - start));
                i = end;
            }
        }
    }

    std::set<std::uint32_t> hashes_;
    std::map<std::uint32_t, std::set<std::string>> matches_;
    std::set<std::string> directories_;
    std::set<std::string> bare_fragments_;
    std::set<std::string> tokens_;
};

struct DecodedRecord {
    std::string sha256;
    std::string detected_type;
};

std::string progress_path(const fs::path& path) {
    return path_utf8(path);
}

void show_progress(std::size_t done, std::size_t total) {
    if (done % 100 == 0 || done == total) {
        std::cerr << "Verified " << done << "/" << total << '\n';
    }
}

std::string entry_json(const Entry& entry, const NameResolver& names,
                       const std::string& output, const std::string& digest,
                       const std::string& detected_type) {
    const std::string name = names.resolved(entry.name_hash);
    const auto candidates = names.candidates(entry.name_hash);
    std::ostringstream json;
    json << "    {\n"
         << "      \"index\": " << entry.index << ",\n"
         << "      \"header_offset\": " << entry.header_offset << ",\n"
         << "      \"original_size\": " << entry.original_size << ",\n"
         << "      \"stored_size\": " << entry.stored_size << ",\n"
         << "      \"checksum\": " << entry.checksum << ",\n"
         << "      \"data_offset\": " << entry.data_offset << ",\n"
         << "      \"compressed_size\": " << entry.compressed_size << ",\n"
         << "      \"name_hash\": " << entry.name_hash << ",\n"
         << "      \"name_hash_hex\": \"" << hex_u32(entry.name_hash).substr(2) << "\",\n"
         << "      \"name\": ";
    if (name.empty()) json << "null";
    else json << '"' << json_escape(name) << '"';
    json << ",\n      \"candidates\": [";
    for (std::size_t i = 0; i < candidates.size(); ++i) {
        if (i != 0) json << ", ";
        json << '"' << json_escape(candidates[i]) << '"';
    }
    json << "],\n"
         << "      \"output\": \"" << json_escape(output) << "\",\n"
         << "      \"sha256\": \"" << digest << "\"";
    if (name.empty()) {
        json << ",\n      \"detected_type\": \"" << json_escape(detected_type) << "\"";
    }
    json << "\n    }";
    return json.str();
}

std::string unknown_types_json(const std::map<std::string, std::size_t>& unknown_types) {
    std::ostringstream json;
    json << "{";
    bool first = true;
    for (const auto& [type, count] : unknown_types) {
        if (!first) json << ",";
        first = false;
        json << "\n    \"" << json_escape(type) << "\": " << count;
    }
    if (!unknown_types.empty()) json << "\n  ";
    json << "}";
    return json.str();
}

std::string summary_json(const fs::path& archive, const std::vector<Entry>& entries,
                         const KeyInfo& key_info, std::size_t verified, const fs::path* output) {
    std::uint64_t original_bytes = 0;
    for (const auto& entry : entries) original_bytes += entry.original_size;
    std::ostringstream json;
    json << "{\n"
         << "  \"archive\": \"" << json_escape(progress_path(archive)) << "\",\n"
         << "  \"files\": " << entries.size() << ",\n"
         << "  \"original_bytes\": " << original_bytes << ",\n"
         << "  \"client_sha256\": \"" << key_info.client_sha256 << "\",\n"
         << "  \"verified\": " << verified;
    if (output != nullptr) json << ",\n  \"output\": \"" << json_escape(progress_path(*output)) << "\"";
    json << "\n}";
    return json.str();
}

bool path_entry_exists(const fs::path& path) {
    std::error_code ec;
    const fs::file_status status = fs::symlink_status(path, ec);
    if (ec == std::errc::no_such_file_or_directory) return false;
    if (ec) throw UnpackError("Cannot inspect output path " + path_utf8(path) + ": " + ec.message());
    return status.type() != fs::file_type::not_found;
}

void rename_no_replace(const fs::path& source, const fs::path& destination) {
#ifdef _WIN32
    if (!MoveFileW(source.c_str(), destination.c_str())) {
        const DWORD code = GetLastError();
        if (code == ERROR_ALREADY_EXISTS || code == ERROR_FILE_EXISTS) {
            throw UnpackError("Output appeared during extraction; refusing to overwrite it: " + path_utf8(destination));
        }
        throw UnpackError("Cannot publish extraction directory: Windows error " + std::to_string(code));
    }
#elif defined(__linux__) && defined(SYS_renameat2)
    if (::syscall(SYS_renameat2, AT_FDCWD, source.c_str(), AT_FDCWD, destination.c_str(), RENAME_NOREPLACE) == 0) {
        return;
    }
    if (errno == EEXIST) {
        throw UnpackError("Output appeared during extraction; refusing to overwrite it: " + path_utf8(destination));
    }
    if (errno != ENOSYS && errno != EINVAL) {
        throw UnpackError("Cannot publish extraction directory: " + std::string(std::strerror(errno)));
    }
    if (path_entry_exists(destination)) {
        throw UnpackError("Output appeared during extraction; refusing to overwrite it: " + path_utf8(destination));
    }
    std::error_code ec;
    fs::rename(source, destination, ec);
    if (ec) throw UnpackError("Cannot publish extraction directory: " + ec.message());
#else
    if (path_entry_exists(destination)) {
        throw UnpackError("Output appeared during extraction; refusing to overwrite it: " + path_utf8(destination));
    }
    std::error_code ec;
    fs::rename(source, destination, ec);
    if (ec) throw UnpackError("Cannot publish extraction directory: " + ec.message());
#endif
}

class TemporaryDirectory {
public:
    explicit TemporaryDirectory(fs::path parent) {
        std::random_device rd;
        std::mt19937_64 rng((static_cast<std::uint64_t>(rd()) << 32) ^ rd() ^
                            static_cast<std::uint64_t>(std::chrono::steady_clock::now().time_since_epoch().count()));
        for (unsigned attempt = 0; attempt < 64; ++attempt) {
            std::ostringstream name;
            name << ".alt2-unpack-" << std::hex << std::setw(16) << std::setfill('0') << rng();
            fs::path candidate = parent / name.str();
            std::error_code ec;
            if (fs::create_directory(candidate, ec)) {
                path_ = std::move(candidate);
                return;
            }
            if (ec && ec != std::errc::file_exists) {
                throw UnpackError("Cannot create temporary directory: " + ec.message());
            }
        }
        throw UnpackError("Cannot reserve a unique temporary extraction directory");
    }
    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;
    ~TemporaryDirectory() {
        if (!path_.empty()) {
            std::error_code ignored;
            fs::remove_all(path_, ignored);
        }
    }
    const fs::path& path() const { return path_; }
private:
    fs::path path_;
};

std::string unknown_filename(const Entry& entry, const std::string& extension) {
    std::ostringstream name;
    name << std::setw(4) << std::setfill('0') << entry.index << "_"
         << std::hex << std::nouppercase << std::setw(8) << std::setfill('0') << entry.name_hash
         << "." << extension;
    return name.str();
}

std::string process_archive(const fs::path& archive, const std::vector<Entry>& entries,
                            const KeyInfo& key_info, NameResolver& names,
                            const fs::path* output) {
    std::ifstream stream(archive, std::ios::binary);
    if (!stream) throw UnpackError("Cannot open archive: " + path_utf8(archive));
    if (output == nullptr) {
        for (const auto& entry : entries) {
            (void)decode_entry(stream, entry, key_info.key);
            show_progress(entry.index + 1, entries.size());
        }
        return summary_json(archive, entries, key_info, entries.size(), nullptr);
    }

    const fs::path final_output = fs::absolute(*output).lexically_normal();
    if (path_entry_exists(final_output)) {
        throw UnpackError("Output already exists (never overwritten): " + path_utf8(final_output));
    }
    fs::path parent = final_output.parent_path();
    if (parent.empty()) parent = fs::current_path();
    std::error_code ec;
    fs::create_directories(parent, ec);
    if (ec) throw UnpackError("Cannot create output parent directory: " + ec.message());
    if (path_entry_exists(final_output)) {
        throw UnpackError("Output already exists (never overwritten): " + path_utf8(final_output));
    }

    TemporaryDirectory temp(parent);
    const fs::path spool = temp.path() / "spool";
    const fs::path result = temp.path() / "result";
    fs::create_directory(spool);
    fs::create_directory(result);
    std::vector<DecodedRecord> records;
    records.reserve(entries.size());
    for (const auto& entry : entries) {
        const Bytes payload = decode_entry(stream, entry, key_info.key);
        records.push_back({sha256_hex(payload), detect_content_type(payload)});
        write_file(spool / std::to_string(entry.index), payload);
        names.scan(payload);
        show_progress(entry.index + 1, entries.size());
    }
    // All payload references are in; try bounded combinations and generation
    // before deciding which entries stay unnamed.
    names.generate();

    std::set<std::string> outputs;
    std::vector<std::string> output_paths;
    output_paths.reserve(entries.size());
    std::map<std::string, std::size_t> unknown_types;
    std::size_t named_count = 0;
    for (const auto& entry : entries) {
        const std::string recovered_name = names.resolved(entry.name_hash);
        std::string relative;
        fs::path relative_path;
        if (!recovered_name.empty()) {
            relative = std::string("files/") + safe_relative_name(recovered_name);
            relative_path = path_from_utf8(relative);
            ++named_count;
        } else {
            const std::string detected = records[entry.index].detected_type;
            ++unknown_types[detected];
            relative = std::string("unknown/") + unknown_filename(entry, type_extension(detected));
            relative_path = path_from_utf8(relative);
        }
        if (!outputs.insert(relative).second) {
            throw UnpackError("Duplicate output path: " + relative);
        }
        const fs::path target = result / relative_path;
        fs::create_directories(target.parent_path(), ec);
        if (ec) throw UnpackError("Cannot create extracted directory: " + ec.message());
        fs::rename(spool / std::to_string(entry.index), target, ec);
        if (ec) throw UnpackError("Cannot move verified file into result: " + ec.message());
        output_paths.push_back(relative);
    }
    const std::size_t unknown_count = entries.size() - named_count;
    std::uint64_t original_bytes = 0;
    for (const auto& entry : entries) original_bytes += entry.original_size;
    std::ostringstream manifest;
    manifest << "{\n"
             << "  \"archive\": \"" << json_escape(progress_path(archive)) << "\",\n"
             << "  \"files\": " << entries.size() << ",\n"
             << "  \"original_bytes\": " << original_bytes << ",\n"
             << "  \"client_sha256\": \"" << key_info.client_sha256 << "\",\n"
             << "  \"verified\": " << entries.size() << ",\n"
             << "  \"named\": " << named_count << ",\n"
             << "  \"unknown\": " << unknown_count << ",\n"
             << "  \"unknown_types\": " << unknown_types_json(unknown_types) << ",\n"
             << "  \"output\": \"" << json_escape(path_utf8(final_output)) << "\",\n"
             << "  \"format\": \"ALT2/XTEA-4/LZ4/XXH32\",\n"
             << "  \"entries\": [\n";
    for (std::size_t i = 0; i < entries.size(); ++i) {
        manifest << entry_json(entries[i], names, output_paths[i], records[i].sha256,
                               records[i].detected_type);
        if (i + 1 != entries.size()) manifest << ',';
        manifest << '\n';
    }
    manifest << "  ]\n}\n";
    const std::string manifest_text = manifest.str();
    {
        std::ofstream manifest_file(result / "manifest.json", std::ios::binary | std::ios::trunc);
        if (!manifest_file) throw UnpackError("Cannot create manifest.json");
        manifest_file.write(manifest_text.data(), static_cast<std::streamsize>(manifest_text.size()));
        manifest_file.flush();
        if (!manifest_file) throw UnpackError("Failed writing manifest.json");
    }
    if (path_entry_exists(final_output)) {
        throw UnpackError("Output appeared during extraction; refusing to overwrite it: " + path_utf8(final_output));
    }
    rename_no_replace(result, final_output);
    // The temporary-directory guard removes the remaining spool and staging directory on return.
    std::ostringstream summary;
    summary << "{\n"
            << "  \"archive\": \"" << json_escape(progress_path(archive)) << "\",\n"
            << "  \"files\": " << entries.size() << ",\n"
            << "  \"original_bytes\": " << original_bytes << ",\n"
            << "  \"client_sha256\": \"" << key_info.client_sha256 << "\",\n"
            << "  \"verified\": " << entries.size() << ",\n"
            << "  \"named\": " << named_count << ",\n"
            << "  \"unknown\": " << unknown_count << ",\n"
            << "  \"unknown_types\": " << unknown_types_json(unknown_types) << ",\n"
            << "  \"output\": \"" << json_escape(path_utf8(final_output)) << "\"\n"
            << "}";
    return summary.str();
}

std::string key_json(const KeyInfo& info) {
    std::ostringstream json;
    json << "{\n"
         << "  \"algorithm\": \"XTEA\",\n"
         << "  \"rounds\": 4,\n"
         << "  \"byte_order\": \"little\",\n"
         << "  \"key_hex\": \"" << hex_bytes(info.key.data(), info.key.size()) << "\",\n"
         << "  \"key_words\": [\"" << hex_u32(info.words[0]) << "\", \""
         << hex_u32(info.words[1]) << "\", \"" << hex_u32(info.words[2]) << "\", \""
         << hex_u32(info.words[3]) << "\"],\n"
         << "  \"key_rva\": \"" << hex_u32(info.key_rva) << "\",\n"
         << "  \"key_file_offset\": \"" << hex_u64(info.key_file_offset) << "\",\n"
         << "  \"loop_rva\": \"" << hex_u32(info.loop_rva) << "\",\n"
         << "  \"client_sha256\": \"" << info.client_sha256 << "\"\n"
         << "}";
    return json.str();
}

std::uint64_t parse_positive_integer(const std::string& text, const std::string& option) {
    std::uint64_t value = 0;
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size() || value == 0) {
        throw UnpackError(option + " must be a positive integer number of bytes");
    }
    return value;
}

struct Options {
    std::string command;
    fs::path archive;
    fs::path client;
    fs::path output;
    std::vector<fs::path> names;
    std::string file_selection;
    std::uint64_t max_file_size = kDefaultMaxFileSize;
    std::uint64_t max_total_size = kDefaultMaxTotalSize;
    bool archive_set = false;
    bool client_set = false;
    bool output_set = false;
    bool all_archives = false;
};

void print_usage(std::ostream& out) {
    out << "ALT2 native unpacker (XTEA-4 / raw LZ4 / XXH32)\n\n"
        << "Usage:\n"
        << "  Alt2Unpacker.exe key [--client PATH]\n"
        << "  Alt2Unpacker.exe list [ARCHIVE|PACK_DIR] [--file NAME | --all] [--client PATH] [--names PATH ...]\n"
        << "                             [--max-file-size BYTES] [--max-total-size BYTES]\n"
        << "  Alt2Unpacker.exe verify [ARCHIVE|PACK_DIR] [--file NAME | --all] [--client PATH]\n"
        << "                             [--max-file-size BYTES] [--max-total-size BYTES]\n"
        << "  Alt2Unpacker.exe extract [ARCHIVE|PACK_DIR] [--file NAME | --all] [--client PATH]\n"
        << "                             [-o DIRECTORY] [--names PATH ...] [--max-file-size BYTES]\n"
        << "                             [--max-total-size BYTES]\n"
        << "  Alt2Unpacker.exe --self-test\n\n"
        << "Running without a command starts extract mode. Directories are searched recursively for ALT2 magic.\n"
        << "With several matches, choose a file name/number interactively or use --file NAME / --all.\n"
        << "Existing output directories are never overwritten. File names are inferred candidates, not stored names.\n";
}

Options parse_options(const std::vector<std::string>& arguments) {
    if (arguments.empty()) {
        print_usage(std::cerr);
        throw UnpackError("Missing command");
    }
    if (arguments[0] == "--help" || arguments[0] == "-h" || arguments[0] == "/?") {
        print_usage(std::cout);
        std::exit(0);
    }
    Options options;
    options.command = arguments[0];
    if (options.command != "key" && options.command != "list" &&
        options.command != "verify" && options.command != "extract") {
        throw UnpackError("Unknown command: " + options.command);
    }
    for (std::size_t i = 1; i < arguments.size(); ++i) {
        const std::string& arg = arguments[i];
        auto value_after = [&](const std::string& option) -> const std::string& {
            if (i + 1 >= arguments.size()) throw UnpackError("Missing value for " + option);
            return arguments[++i];
        };
        if (arg == "--client") {
            options.client = path_from_utf8(value_after(arg));
            options.client_set = true;
        } else if (arg == "--names") {
            options.names.push_back(path_from_utf8(value_after(arg)));
        } else if (arg == "--file") {
            options.file_selection = value_after(arg);
        } else if (arg == "--all") {
            options.all_archives = true;
        } else if (arg == "--max-file-size") {
            options.max_file_size = parse_positive_integer(value_after(arg), arg);
        } else if (arg == "--max-total-size") {
            options.max_total_size = parse_positive_integer(value_after(arg), arg);
        } else if (arg == "-o" || arg == "--output") {
            options.output = path_from_utf8(value_after(arg));
            options.output_set = true;
        } else if (!arg.empty() && arg[0] == '-') {
            throw UnpackError("Unknown option: " + arg);
        } else if (!options.archive_set && options.command != "key") {
            options.archive = path_from_utf8(arg);
            options.archive_set = true;
        } else {
            throw UnpackError("Unexpected argument: " + arg);
        }
    }
    if (options.command == "key" && (options.archive_set || options.output_set || !options.names.empty() ||
                                      !options.file_selection.empty() || options.all_archives)) {
        throw UnpackError("The key command accepts only --client");
    }
    if (options.command != "extract" && options.output_set) {
        throw UnpackError("--output is supported only by extract");
    }
    if (options.command == "verify" && !options.names.empty()) {
        throw UnpackError("--names is supported only by list and extract");
    }
    if (!options.file_selection.empty() && options.all_archives) {
        throw UnpackError("Use either --file NAME or --all, not both");
    }
    return options;
}

bool is_directory_path(const fs::path& path) {
    std::error_code ec;
    return fs::is_directory(path, ec) && !ec;
}

fs::path find_alt2_root(const fs::path& executable) {
    std::error_code ec;
    fs::path current = fs::absolute(executable, ec);
    if (ec) current = executable;
    if (!current.empty() && current.has_filename()) current = current.parent_path();
    for (unsigned i = 0; i < 10 && !current.empty(); ++i) {
        const bool has_pack_dir = is_directory_path(current / "data") || is_directory_path(current / "pack");
        if (fs::exists(current / "metin2client.exe") && has_pack_dir) {
            return current;
        }
        const fs::path parent = current.parent_path();
        if (parent == current) break;
        current = parent;
    }
    const fs::path cwd = fs::current_path(ec);
    if (!ec && fs::exists(cwd / "alt2" / "metin2client.exe")) return cwd / "alt2";
    if (!ec && fs::exists(cwd / "metin2client.exe")) return cwd;
    return cwd / "alt2";
}

fs::path default_pack_source(const fs::path& root) {
    if (is_directory_path(root / "pack")) return root / "pack";
    if (is_directory_path(root / "data")) return root / "data";
    return root / "data";
}

bool has_alt2_magic(const fs::path& file) {
    std::error_code ec;
    if (fs::file_size(file, ec) < 4 || ec) return false;
    std::ifstream stream(file, std::ios::binary);
    if (!stream) return false;
    std::array<std::uint8_t, 4> bytes{};
    stream.read(reinterpret_cast<char*>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
    return stream.gcount() == static_cast<std::streamsize>(bytes.size()) && read_u32_ptr(bytes.data()) == kMagic;
}

std::vector<fs::path> discover_archives(const fs::path& directory) {
    if (!is_directory_path(directory)) {
        throw UnpackError("Pack directory does not exist or is not a directory: " + path_utf8(directory));
    }
    std::vector<fs::path> archives;
    std::error_code ec;
    fs::recursive_directory_iterator it(directory, fs::directory_options::skip_permission_denied, ec);
    const fs::recursive_directory_iterator end;
    if (ec) throw UnpackError("Cannot scan pack directory: " + ec.message());
    while (it != end) {
        const fs::directory_entry item = *it;
        std::error_code status_error;
        const auto status = item.symlink_status(status_error);
        if (!status_error && status.type() == fs::file_type::regular && has_alt2_magic(item.path())) {
            archives.push_back(item.path());
        }
        it.increment(ec);
        if (ec) {
            ec.clear();
        }
    }
    std::sort(archives.begin(), archives.end(), [&](const fs::path& left, const fs::path& right) {
        return path_utf8(left.lexically_relative(directory)) < path_utf8(right.lexically_relative(directory));
    });
    return archives;
}

std::string trim_cli_text(std::string_view value) {
    std::size_t begin = 0;
    while (begin < value.size() && (value[begin] == ' ' || value[begin] == '\t' || value[begin] == '\r' || value[begin] == '\n')) ++begin;
    std::size_t end = value.size();
    while (end > begin && (value[end - 1] == ' ' || value[end - 1] == '\t' || value[end - 1] == '\r' || value[end - 1] == '\n')) --end;
    return std::string(value.substr(begin, end - begin));
}

std::string selector_normalize(std::string value) {
    value = normalize_name(std::move(value));
    while (value.rfind("./", 0) == 0) value.erase(0, 2);
    return value;
}

std::string archive_relative_label(const fs::path& archive, const fs::path& source) {
    const fs::path relative = is_directory_path(source) ? archive.lexically_relative(source) : archive.filename();
    return path_utf8(relative.empty() ? archive.filename() : relative);
}

std::string archive_output_name(const fs::path& archive, const fs::path& source) {
    fs::path relative = is_directory_path(source) ? archive.lexically_relative(source) : archive.filename();
    if (relative.empty()) relative = archive.filename();
    relative.replace_extension();
    std::string name = path_utf8(relative);
    if (name.empty()) throw UnpackError("Cannot derive an output folder for archive: " + path_utf8(archive));
    return safe_relative_name(std::move(name));
}

std::vector<fs::path> select_archives(const fs::path& source, const Options& options) {
    std::vector<fs::path> candidates;
    const bool source_is_directory = is_directory_path(source);
    if (!source_is_directory) {
        if (options.all_archives || !options.file_selection.empty()) {
            throw UnpackError("--all and --file NAME require a pack directory as input");
        }
        if (!fs::exists(source)) throw UnpackError("Archive does not exist: " + path_utf8(source));
        return {source};
    }
    candidates = discover_archives(source);
    if (candidates.empty()) {
        throw UnpackError("No ALT2 archives (magic 0x000fed0c) were found in: " + path_utf8(source));
    }
    if (options.all_archives) return candidates;

    auto match_name = [&](const std::string& selector) {
        const std::string wanted = selector_normalize(selector);
        std::vector<fs::path> matched;
        for (const auto& candidate : candidates) {
            const std::string relative = selector_normalize(path_utf8(candidate.lexically_relative(source)));
            const std::string filename = selector_normalize(path_utf8(candidate.filename()));
            const std::string stem = selector_normalize(path_utf8(candidate.stem()));
            if (wanted == relative || wanted == filename || wanted == stem) matched.push_back(candidate);
        }
        return matched;
    };
    if (!options.file_selection.empty()) {
        auto matched = match_name(options.file_selection);
        if (matched.empty()) throw UnpackError("No ALT2 archive matches --file " + options.file_selection);
        if (matched.size() > 1) {
            throw UnpackError("--file name is ambiguous; provide a relative path instead of a basename");
        }
        return matched;
    }
    if (candidates.size() == 1) return candidates;

    std::cerr << "ALT2 archives found: " << candidates.size() << '\n';
    for (std::size_t i = 0; i < candidates.size(); ++i) {
        std::error_code ec;
        const auto size = fs::file_size(candidates[i], ec);
        std::cerr << "  [" << (i + 1) << "] " << archive_relative_label(candidates[i], source);
        if (!ec) std::cerr << " (" << size << " bytes)";
        std::cerr << '\n';
    }
    std::cerr << "Enter a file name, number, comma-separated numbers, or 'all': " << std::flush;
    std::string answer;
    if (!std::getline(std::cin, answer)) {
        throw UnpackError("No selection was entered; rerun with --file NAME or --all");
    }
    answer = trim_cli_text(answer);
    const std::string lowered = selector_normalize(answer);
    if (lowered == "all" || lowered == "a") return candidates;
    if (answer.empty()) throw UnpackError("Empty selection; rerun with --file NAME or --all");

    bool numeric_selection = true;
    std::set<std::size_t> indexes;
    std::size_t begin = 0;
    while (begin <= answer.size()) {
        const std::size_t comma = answer.find(',', begin);
        const std::string item = trim_cli_text(std::string_view(answer).substr(
            begin, comma == std::string::npos ? std::string::npos : comma - begin));
        std::size_t number = 0;
        if (item.empty()) {
            numeric_selection = false;
            break;
        }
        for (unsigned char c : item) {
            if (!ascii_digit(c)) { numeric_selection = false; break; }
            number = number * 10 + static_cast<std::size_t>(c - '0');
        }
        if (!numeric_selection || number == 0 || number > candidates.size()) {
            numeric_selection = false;
            break;
        }
        indexes.insert(number - 1);
        if (comma == std::string::npos) break;
        begin = comma + 1;
    }
    if (numeric_selection && !indexes.empty()) {
        std::vector<fs::path> selected;
        for (const auto index : indexes) selected.push_back(candidates[index]);
        return selected;
    }
    auto matched = match_name(answer);
    if (matched.empty()) {
        throw UnpackError("Selection did not match a pack; enter a listed name/number or 'all'");
    }
    if (matched.size() > 1) {
        throw UnpackError("That filename is ambiguous; select its listed number or relative path");
    }
    return matched;
}

void list_archive(const std::vector<Entry>& entries, const NameResolver& names) {
    std::cout << "INDEX\tNAME_HASH\tORIGINAL\tCOMPRESSED\tSTORED\tNAME (unverified payload)\n";
    for (const auto& entry : entries) {
        const std::string name = names.resolved(entry.name_hash);
        std::cout << entry.index << '\t' << std::hex << std::nouppercase << std::setw(8) << std::setfill('0')
                  << entry.name_hash << std::dec << std::setfill(' ') << '\t'
                  << entry.original_size << '\t' << entry.compressed_size << '\t' << entry.stored_size << '\t'
                  << (name.empty() ? "-" : name) << '\n';
    }
}

void run_content_type_tests();
void run_name_generation_tests();

void run_self_tests() {
    const std::array<std::uint8_t, 16> key{
        0x54, 0xd8, 0x20, 0x39, 0xaa, 0x8d, 0x27, 0x22,
        0xdc, 0x23, 0xe8, 0x1c, 0x69, 0x6b, 0x74, 0x30};
    const Bytes known_cipher{0x17, 0x8b, 0x82, 0xd7, 0x29, 0x96, 0x02, 0x59};
    const Bytes known_plain{0xb7, 0x53, 0x63, 0x72, 0x69, 0x70, 0x74, 0x54};
    if (decrypt_xtea4(known_cipher, key) != known_plain) {
        throw UnpackError("Self-test failed: supplied XTEA-4 known vector");
    }
    Bytes sequence(256);
    for (std::size_t i = 0; i < sequence.size(); ++i) sequence[i] = static_cast<std::uint8_t>(i);
    if (decrypt_xtea4(encrypt_xtea4_for_test(sequence, key), key) != sequence) {
        throw UnpackError("Self-test failed: XTEA-4 round trip");
    }
    const Bytes lz4_literal{0x50, 'h', 'e', 'l', 'l', 'o'};
    const Bytes hello{'h', 'e', 'l', 'l', 'o'};
    if (lz4_decompress_block(lz4_literal.data(), lz4_literal.size(), hello.size()) != hello) {
        throw UnpackError("Self-test failed: raw LZ4 literal block");
    }
    const std::string abc = "abc";
    if (sha256_hex(reinterpret_cast<const std::uint8_t*>(abc.data()), abc.size()) !=
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad") {
        throw UnpackError("Self-test failed: SHA-256");
    }
    if (crc32("assassin_m.msm") != 0x6E2DEEFDu) {
        throw UnpackError("Self-test failed: filename CRC32");
    }
    if (xxh32(hello.data(), hello.size(), kMagic) != 0x3BF12B23u) {
        throw UnpackError("Self-test failed: seeded XXH32 reference vector");
    }
    run_content_type_tests();
    run_name_generation_tests();
    std::cout << "Self-test passed.\n";
}

void expect_content_type(const Bytes& data, const std::string& expected) {
    const std::string detected = detect_content_type(data);
    if (detected != expected) {
        throw UnpackError("Self-test failed: content type " + detected +
                          " instead of " + expected);
    }
}

void run_content_type_tests() {
    Bytes png;
    for (const std::uint8_t byte : {0x89u, 0x50u, 0x4Eu, 0x47u, 0x0Du, 0x0Au, 0x1Au, 0x0Au}) {
        png.push_back(byte);
    }
    png.resize(24, 0);
    expect_content_type(png, "png");
    Bytes jpeg{0xFF, 0xD8, 0xFF, 0xE0};
    jpeg.resize(24, 0);
    expect_content_type(jpeg, "jpg");
    expect_content_type(Bytes{}, "empty");
    expect_content_type(Bytes(24, 0x41), "txt");
    expect_content_type(Bytes{'i', 'm', 'p', 'o', 'r', 't', ' ', 'a', 'p', 'p', '\r', '\n',
                              'i', 'm', 'p', 'o', 'r', 't', ' ', 'u', 'i', '\r', '\n'}, "py");
    const std::string script = "ScriptType            RaceDataScript\r\nBaseModelFileName   x\r\n";
    expect_content_type(Bytes(script.begin(), script.end()), "msm");
    const std::string motion = "ScriptType            RaceDataScript\r\nMotionFileName   y\r\n";
    expect_content_type(Bytes(motion.begin(), motion.end()), "msa");
    Bytes tga_footer(32, 0);
    const std::string footer("TRUEVISION-XFILE.\x00", 18);
    tga_footer.insert(tga_footer.end(), footer.begin(), footer.end());
    expect_content_type(tga_footer, "tga");
    Bytes binary{0x00, 0x01, 0x02, 0x03, 0x7F, 0x80, 0xFF};
    binary.resize(24, 0x00);
    expect_content_type(binary, "bin");
}

void run_name_generation_tests() {
    // Cross-file combination: directory from one scan, bare name from another.
    const std::uint32_t board_hash = name_hash("skill_tree/board/top.tga");
    NameResolver board_entries((std::set<std::uint32_t>{board_hash}));
    board_entries.scan(Bytes{'p', 'a', 't', 'h', ' ', '=', ' ', '"', 's', 'k', 'i', 'l', 'l', '_',
                             't', 'r', 'e', 'e', '/', 'b', 'o', 'a', 'r', 'd', '/', '"', '\n'});
    if (!board_entries.resolved(board_hash).empty()) {
        throw UnpackError("Self-test failed: combination ran before generate()");
    }
    board_entries.scan(Bytes{'l', 'i', 'n', 'k', ' ', 'h', 'r', 'e', 'f', '=', '"', 't', 'o', 'p',
                             '.', 't', 'g', 'a', '"', '\n'});
    board_entries.generate();
    if (board_entries.resolved(board_hash) != "skill_tree/board/top.tga") {
        throw UnpackError("Self-test failed: cross-file directory + fragment generation");
    }
    // Exhaustive short stems with an observed directory.
    const std::uint32_t direction_hash = name_hash("skill_tree/direction/7.tga");
    NameResolver stem_entries((std::set<std::uint32_t>{direction_hash}));
    const std::string stem_data = "dir = \"skill_tree/direction/\"\n";
    stem_entries.scan(Bytes(stem_data.begin(), stem_data.end()));
    stem_entries.generate();
    if (stem_entries.resolved(direction_hash) != "skill_tree/direction/7.tga") {
        throw UnpackError("Self-test failed: short-stem generation");
    }
    // Identifier token + extension and the ui prefix.
    const std::uint32_t token_hash = name_hash("uiskyboxchanger.py");
    NameResolver token_entries((std::set<std::uint32_t>{token_hash}));
    const std::string token_data = "self.handler = SkyBoxChanger()\n";
    token_entries.scan(Bytes(token_data.begin(), token_data.end()));
    token_entries.generate();
    if (token_entries.resolved(token_hash) != "uiskyboxchanger.py") {
        throw UnpackError("Self-test failed: token + extension generation");
    }
    // CRC-checked candidates never invent names for unmatched hashes.
    NameResolver absent_entries((std::set<std::uint32_t>{0x11223344u, 0x55667788u}));
    const std::string noise = "A = \"ui/\"\nbackground.png\nSkyBoxChanger()\n";
    absent_entries.scan(Bytes(noise.begin(), noise.end()));
    absent_entries.generate();
    if (!absent_entries.candidates(0x11223344u).empty() || !absent_entries.candidates(0x55667788u).empty()) {
        throw UnpackError("Self-test failed: generation invented a name");
    }
}

int run(const std::vector<std::string>& arguments, const std::string& executable) {
    if (arguments.size() == 1 && arguments[0] == "--self-test") {
        run_self_tests();
        return 0;
    }
    const std::vector<std::string> default_extract_command{"extract"};
    const std::vector<std::string>& command_arguments = arguments.empty() ? default_extract_command : arguments;
    if (arguments.empty()) {
        std::cerr << "No command supplied; starting extract mode.\n";
    }
    Options options = parse_options(command_arguments);
    const fs::path root = find_alt2_root(path_from_utf8(executable));
    if (!options.client_set) options.client = root / "metin2client.exe";
    if (options.command != "key" && !options.archive_set) options.archive = default_pack_source(root);

    const Bytes client = read_file(options.client);
    if (options.command == "key") {
        std::cout << key_json(discover_key(client)) << '\n';
        return 0;
    }
    const std::vector<fs::path> archives = select_archives(options.archive, options);
    if (options.command == "list") {
        for (std::size_t i = 0; i < archives.size(); ++i) {
            if (archives.size() > 1) {
                std::cout << "\n=== " << archive_relative_label(archives[i], options.archive) << " ===\n";
            }
            const auto entries = read_index(archives[i], options.max_file_size, options.max_total_size);
            NameResolver names(entries);
            names.scan(client);
            for (const auto& names_file : options.names) names.load(names_file);
            names.generate();
            list_archive(entries, names);
        }
        return 0;
    }

    const KeyInfo key_info = discover_key(client);
    std::vector<std::vector<Entry>> indexes;
    indexes.reserve(archives.size());
    for (const auto& archive : archives) {
        indexes.push_back(read_index(archive, options.max_file_size, options.max_total_size));
    }

    std::vector<fs::path> outputs;
    if (options.command == "extract") {
        outputs.reserve(archives.size());
        std::set<std::string> unique_outputs;
        for (const auto& archive : archives) {
            fs::path output;
            if (options.output_set && archives.size() == 1) {
                output = options.output;
            } else {
                const fs::path pack_name = path_from_utf8(archive_output_name(archive, options.archive));
                output = (options.output_set ? options.output : root / "unpacked") / pack_name;
            }
            output = fs::absolute(output).lexically_normal();
            const std::string output_key = selector_normalize(path_utf8(output));
            if (!unique_outputs.insert(output_key).second) {
                throw UnpackError("Selected packs resolve to the same output directory: " + path_utf8(output));
            }
            if (path_entry_exists(output)) {
                throw UnpackError("Output already exists (never overwritten): " + path_utf8(output));
            }
            outputs.push_back(std::move(output));
        }
        if (archives.size() > 1) {
            std::cerr << "Pre-verifying all selected archives before publishing any output...\n";
            for (std::size_t i = 0; i < archives.size(); ++i) {
                NameResolver preverify_names(indexes[i]);
                (void)process_archive(archives[i], indexes[i], key_info, preverify_names, nullptr);
            }
        }
    }

    std::vector<std::string> summaries;
    summaries.reserve(archives.size());
    for (std::size_t i = 0; i < archives.size(); ++i) {
        NameResolver names(indexes[i]);
        if (options.command == "extract") names.scan(client);
        for (const auto& names_file : options.names) names.load(names_file);
        const fs::path* output = options.command == "extract" ? &outputs[i] : nullptr;
        summaries.push_back(process_archive(archives[i], indexes[i], key_info, names, output));
    }
    if (summaries.size() == 1) {
        std::cout << summaries.front() << '\n';
    } else {
        std::cout << "[\n";
        for (std::size_t i = 0; i < summaries.size(); ++i) {
            std::cout << summaries[i] << (i + 1 == summaries.size() ? "\n" : ",\n");
        }
        std::cout << "]\n";
    }
    return 0;
}

} // namespace alt2

#ifdef _WIN32
std::string wide_to_utf8(const wchar_t* value) {
    if (value == nullptr) return {};
    const int required = WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, value, -1, nullptr, 0, nullptr, nullptr);
    if (required <= 0) throw alt2::UnpackError("Could not convert a Windows command-line argument to UTF-8");
    std::string result(static_cast<std::size_t>(required), '\0');
    if (WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, value, -1,
                            result.data(), required, nullptr, nullptr) <= 0) {
        throw alt2::UnpackError("Could not convert a Windows command-line argument to UTF-8");
    }
    result.resize(static_cast<std::size_t>(required - 1));
    return result;
}

int wmain(int argc, wchar_t** argv) {
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    try {
        std::vector<std::string> arguments;
        arguments.reserve(static_cast<std::size_t>(argc > 0 ? argc - 1 : 0));
        for (int i = 1; i < argc; ++i) arguments.push_back(wide_to_utf8(argv[i]));
        const std::string executable = argc > 0 ? wide_to_utf8(argv[0]) : "Alt2Unpacker.exe";
        return alt2::run(arguments, executable);
    } catch (const alt2::UnpackError& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
#else
int main(int argc, char** argv) {
    try {
        std::vector<std::string> arguments;
        arguments.reserve(static_cast<std::size_t>(argc > 0 ? argc - 1 : 0));
        for (int i = 1; i < argc; ++i) arguments.emplace_back(argv[i]);
        const std::string executable = argc > 0 ? argv[0] : "Alt2Unpacker";
        return alt2::run(arguments, executable);
    } catch (const alt2::UnpackError& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
#endif
