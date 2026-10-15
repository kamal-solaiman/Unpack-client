// testarchive: builds small valid History D2 archives for integration tests.
// Usage: testarchive OUT.d2 NAME1=FILE1 [NAME2=FILE2 ...]
// Same primitives as the unpacker (vendored tiny-AES / xxHash), so any
// archive it produces must decode and verify with HistoryUnpacker itself.
#include <cstdio>
#include <cstring>
#include <algorithm>
#include <array>
#include <string>
#include <vector>
extern "C" {
#include "aes.h"
}
#define XXH_INLINE_ALL
#include "xxhash.h"
using Bytes = std::vector<uint8_t>;

static void wr32(Bytes& b, uint32_t v) { for (int i = 0; i < 4; ++i) b.push_back(uint8_t(v >> (i * 8))); }
static std::string lowerSlashes(std::string s) { for (char& c : s) { if (c == '\\') c = '/'; if (c >= 'A' && c <= 'Z') c = char(c - 'A' + 'a'); } return s; }
static uint32_t crc32n(const std::string& s) {
    uint32_t crc = 0xffffffffu;
    for (unsigned char c : lowerSlashes(s)) { crc ^= c; for (int i = 0; i < 8; ++i) crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u))); }
    return ~crc;
}
// CFB128 encryption (mirror of history.cpp decrypt()).
static Bytes cfbEncrypt(const Bytes& in, const std::array<uint8_t, 32>& key, const std::array<uint8_t, 16>& iv) {
    AES_ctx ctx{}; AES_init_ctx(&ctx, key.data());
    auto feedback = iv; Bytes out(in.size());
    for (size_t pos = 0; pos < in.size(); pos += 16) {
        auto stream = feedback; AES_ECB_encrypt(&ctx, stream.data());
        size_t count = std::min(size_t(16), in.size() - pos);
        for (size_t j = 0; j < count; ++j) { out[pos + j] = in[pos + j] ^ stream[j]; feedback[j] = out[pos + j]; }
    }
    return out;
}
static Bytes readFile(const char* path) {
    FILE* f = std::fopen(path, "rb"); if (!f) { std::fprintf(stderr, "cannot open %s\n", path); std::exit(2); }
    std::fseek(f, 0, SEEK_END); long n = std::ftell(f); std::fseek(f, 0, SEEK_SET);
    Bytes b(static_cast<size_t>(n)); if (n) std::fread(b.data(), 1, b.size(), f); std::fclose(f); return b;
}
int main(int argc, char** argv) {
    if (argc < 3) { std::fprintf(stderr, "usage: testarchive OUT.d2 NAME=FILE...\n"); return 2; }
    std::array<uint8_t, 32> key{}; std::array<uint8_t, 16> iv{};
    for (int i = 0; i < 32; ++i) key[size_t(i)] = uint8_t(i);
    for (int i = 0; i < 16; ++i) iv[size_t(i)] = uint8_t(32 + i);
    struct Item { std::string name; Bytes payload; };
    std::vector<Item> items;
    for (int i = 2; i < argc; ++i) {
        std::string a = argv[i]; auto eq = a.find('=');
        if (eq == std::string::npos) { std::fprintf(stderr, "bad NAME=FILE: %s\n", argv[i]); return 2; }
        items.push_back({a.substr(0, eq), readFile(a.c_str() + eq + 1)});
    }
    const uint32_t magic = 0xf00fed5cu;
    Bytes out; wr32(out, magic); out.insert(out.end(), key.begin(), key.end());
    out.insert(out.end(), iv.begin(), iv.end()); out.resize(68, 0); // IV field is 32 bytes; CFB uses the first 16
    for (const auto& item : items) {
        Bytes stored = cfbEncrypt(item.payload, key, iv);
        uint32_t recordStart = uint32_t(out.size());
        wr32(out, uint32_t(item.payload.size()));
        wr32(out, XXH32(item.payload.data(), item.payload.size(), magic));
        wr32(out, recordStart + 20);              // absolute payload offset
        wr32(out, uint32_t(stored.size()));
        wr32(out, crc32n(item.name));
        out.insert(out.end(), stored.begin(), stored.end());
    }
    FILE* f = std::fopen(argv[1], "wb"); if (!f) { std::fprintf(stderr, "cannot create %s\n", argv[1]); return 2; }
    std::fwrite(out.data(), 1, out.size(), f); std::fclose(f);
    std::printf("%s: %zu bytes, %zu entries\n", argv[1], out.size(), items.size());
    return 0;
}
