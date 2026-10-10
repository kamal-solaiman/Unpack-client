// SPDX-License-Identifier: MIT
#include "snappy.h"

#include <algorithm>
#include <cstring>

namespace m2 {
namespace {

constexpr uint32_t kFramedMagic[6] = {0xFF, 0x06, 0x00, 0x00, 0x00, 0x00};

bool readVarint(const uint8_t* in, size_t inLen, size_t& ip, uint64_t& value) {
    value = 0;
    int shift = 0;
    while (ip < inLen) {
        uint8_t b = in[ip++];
        value |= static_cast<uint64_t>(b & 0x7F) << shift;
        if ((b & 0x80) == 0) return true;
        shift += 7;
        if (shift > 63) return false;
    }
    return false;
}

void writeVarint(uint64_t value, Bytes& out) {
    while (value >= 0x80) {
        out.push_back(static_cast<uint8_t>(value | 0x80));
        value >>= 7;
    }
    out.push_back(static_cast<uint8_t>(value));
}

// Decompresses one raw snappy block into out (appending).
bool decodeRawBlock(const uint8_t* in, size_t inLen, Bytes& out, std::string* err) {
    auto fail = [&](const std::string& what) {
        if (err) *err = what;
        return false;
    };
    size_t ip = 0;
    uint64_t expected = 0;
    if (!readVarint(in, inLen, ip, expected)) return fail("snappy: truncated length preamble");
    const size_t start = out.size();
    out.resize(start + static_cast<size_t>(expected));
    uint8_t* op = out.data() + start;
    size_t produced = 0;

    while (ip < inLen) {
        uint8_t tag = in[ip++];
        switch (tag & 3) {
            case 0: {  // literal
                size_t len = tag >> 2;
                if (len < 60) {
                    len += 1;
                } else {
                    const size_t extra = len - 59;  // 1..4
                    if (ip + extra > inLen) return fail("snappy: truncated literal length");
                    uint64_t v = 0;
                    for (size_t i = 0; i < extra; ++i) v |= static_cast<uint64_t>(in[ip + i]) << (8 * i);
                    ip += extra;
                    len = static_cast<size_t>(v) + 1;
                }
                if (ip + len > inLen) return fail("snappy: truncated literal data");
                if (produced + len > expected) return fail("snappy: output overrun");
                std::memcpy(op + produced, in + ip, len);
                ip += len;
                produced += len;
                break;
            }
            case 1: {  // copy with 1 byte offset
                size_t len = ((tag >> 2) & 7) + 4;
                if (ip + 1 > inLen) return fail("snappy: truncated copy1");
                size_t offset = (static_cast<size_t>(tag & 0xE0) << 3) | in[ip++];
                if (offset == 0 || offset > produced) return fail("snappy: bad copy1 offset");
                if (produced + len > expected) return fail("snappy: output overrun");
                const uint8_t* src = op + produced - offset;
                for (size_t i = 0; i < len; ++i) op[produced + i] = src[i];
                produced += len;
                break;
            }
            case 2:  // copy with 2 byte offset
            case 3: {  // copy with 4 byte offset
                const size_t offsetBytes = (tag & 3) == 2 ? 2 : 4;
                size_t len = (tag >> 2) + 1;
                if (ip + offsetBytes > inLen) return fail("snappy: truncated copy offset");
                uint64_t offset = 0;
                for (size_t i = 0; i < offsetBytes; ++i)
                    offset |= static_cast<uint64_t>(in[ip + i]) << (8 * i);
                ip += offsetBytes;
                if (offset == 0 || offset > produced) return fail("snappy: bad copy offset");
                if (produced + len > expected) return fail("snappy: output overrun");
                const uint8_t* src = op + produced - static_cast<size_t>(offset);
                for (size_t i = 0; i < len; ++i) op[produced + i] = src[i];
                produced += len;
                break;
            }
        }
    }
    if (produced != expected) return fail("snappy: size mismatch");
    out.resize(start + produced);
    return true;
}

}  // namespace

bool snappyLooksFramed(const uint8_t* in, size_t inLen) {
    if (inLen < 10) return false;
    for (int i = 0; i < 6; ++i)
        if (in[i] != static_cast<uint8_t>(kFramedMagic[i])) return false;
    return in[6] == 's' && in[7] == 'N' && in[8] == 'a' && in[9] == 'p';
}

bool snappyUncompressedLength(const uint8_t* in, size_t inLen, size_t& length, std::string* err) {
    size_t ip = 0;
    uint64_t v = 0;
    if (!readVarint(in, inLen, ip, v)) {
        if (err) *err = "snappy: truncated length preamble";
        return false;
    }
    length = static_cast<size_t>(v);
    return true;
}

bool snappyDecompress(const uint8_t* in, size_t inLen, uint8_t* out, size_t outCap,
                      size_t& outLen, std::string* err) {
    Bytes buf;
    buf.reserve(outCap ? outCap : inLen * 2);
    if (!decodeRawBlock(in, inLen, buf, err)) return false;
    if (buf.size() > outCap) {
        if (err) *err = "snappy: output buffer too small";
        return false;
    }
    if (!buf.empty() && out) std::memcpy(out, buf.data(), buf.size());
    outLen = buf.size();
    return true;
}

bool snappyDecompressTo(const uint8_t* in, size_t inLen, size_t expectedSize, Bytes& out,
                        std::string* err) {
    out.clear();
    if (snappyLooksFramed(in, inLen)) {
        // Framed format: magic + [chunk type(1) length(3) payload...]*
        size_t ip = 10;
        while (ip + 4 <= inLen) {
            uint8_t type = in[ip];
            uint32_t len = static_cast<uint32_t>(in[ip + 1]) |
                           (static_cast<uint32_t>(in[ip + 2]) << 8) |
                           (static_cast<uint32_t>(in[ip + 3]) << 16);
            ip += 4;
            if (ip + len > inLen) {
                if (err) *err = "snappy: truncated frame";
                return false;
            }
            if (type == 0x00) {  // uncompressed data
                if (!decodeRawBlock(in + ip, len, out, err)) return false;
            } else if (type == 0x01) {  // compressed data (already deframed)
                Bytes block;
                if (!decodeRawBlock(in + ip, len, block, err)) return false;
                out.insert(out.end(), block.begin(), block.end());
            }
            // 0xff (stream identifier) and padding chunks are skipped.
            ip += len;
        }
        if (expectedSize && out.size() != expectedSize) {
            if (err) *err = "snappy: framed size mismatch";
            return false;
        }
        return true;
    }

    size_t declared = 0;
    if (!snappyUncompressedLength(in, inLen, declared, err)) return false;
    if (expectedSize && declared != expectedSize) {
        if (err) *err = "snappy: declared size does not match the index entry";
        return false;
    }
    return decodeRawBlock(in, inLen, out, err);
}

bool snappyStore(const uint8_t* in, size_t inLen, Bytes& out) {
    out.clear();
    writeVarint(inLen, out);
    size_t pos = 0;
    while (pos < inLen) {
        size_t chunk = std::min<size_t>(inLen - pos, 1u << 20);
        size_t v = chunk - 1;
        if (v < 60) {
            out.push_back(static_cast<uint8_t>(v << 2));
        } else {
            size_t extra = 1;
            while ((v >> (8 * extra)) != 0) ++extra;
            if (extra > 4) return false;
            out.push_back(static_cast<uint8_t>(((59 + extra) << 2)));
            for (size_t i = 0; i < extra; ++i)
                out.push_back(static_cast<uint8_t>((v >> (8 * i)) & 0xFF));
        }
        out.insert(out.end(), in + pos, in + pos + chunk);
        pos += chunk;
    }
    return true;
}

}  // namespace m2
