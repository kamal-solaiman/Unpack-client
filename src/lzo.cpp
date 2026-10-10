// SPDX-License-Identifier: MIT
#include "lzo.h"

#include <cstring>

namespace m2 {
namespace {

constexpr size_t kM2MaxOffset = 0x0800;
constexpr size_t kM4ExtraOffset = 0x4000;

inline void copyMatch(uint8_t* dst, const uint8_t* src, size_t n) {
    // Source and destination overlap for short distances: copy forwards, byte
    // by byte, exactly like the reference decoder does.
    for (size_t i = 0; i < n; ++i) dst[i] = src[i];
}

}  // namespace

bool lzo1xDecompress(const uint8_t* in, size_t inLen, uint8_t* out, size_t outCap,
                     size_t& outLen, std::string* err) {
    outLen = 0;
    auto fail = [&](const std::string& what) {
        if (err) *err = what;
        return false;
    };
    if (!in || inLen == 0) return fail("lzo: empty input");
    if (!out && outCap != 0) return fail("lzo: null output");

    size_t ip = 0, op = 0, t = 0;
    int64_t mPos = 0;

    // The first token is only consumed here when it encodes a literal run that
    // is longer than the main loop can express (> 17); otherwise the main loop
    // reads it as its own token.
    if (in[0] > 17) {
        t = static_cast<size_t>(in[ip++]) - 17;
        if (t == 0) return fail("lzo: invalid first token");
        if (t >= 4) {
            if (ip + t > inLen || op + t > outCap) return fail("lzo: overrun in first literal run");
            std::memcpy(out + op, in + ip, t);
            op += t;
            ip += t;
            goto first_literal_run;
        }
        goto match_next;
    }

    for (;;) {
        if (ip >= inLen) return fail("lzo: unexpected end of input");
        t = in[ip++];
        if (t >= 16) goto match;

        // Long literal run: t + 3 bytes (t == 0 means the length continues in
        // the following zero bytes).
        if (t == 0) {
            while (ip < inLen && in[ip] == 0) {
                t += 255;
                ++ip;
            }
            if (ip >= inLen) return fail("lzo: truncated literal run length");
            t += 15 + in[ip++];
        }
        t += 3;
        if (ip + t > inLen || op + t > outCap) return fail("lzo: overrun in literal run");
        std::memcpy(out + op, in + ip, t);
        op += t;
        ip += t;

    first_literal_run:
        if (ip + 2 > inLen) return fail("lzo: truncated first literal run");
        t = in[ip++];
        if (t >= 16) goto match;

        // Three byte match, distance in [0x0801, 0x1000].
        mPos = static_cast<int64_t>(op) - static_cast<int64_t>(1 + kM2MaxOffset);
        mPos -= static_cast<int64_t>(t >> 2);
        mPos -= static_cast<int64_t>(in[ip++]) << 2;
        if (mPos < 0 || static_cast<uint64_t>(mPos) >= op) return fail("lzo: bad match distance");
        if (op + 3 > outCap) return fail("lzo: output overrun");
        copyMatch(out + op, out + mPos, 3);
        op += 3;
        goto match_done;

        for (;;) {
        match:
            if (t >= 64) {  // M2: 2 byte token, length 2..8
                if (ip + 1 > inLen) return fail("lzo: truncated M2 match");
                mPos = static_cast<int64_t>(op) - 1;
                mPos -= static_cast<int64_t>((t >> 2) & 7);
                mPos -= static_cast<int64_t>(in[ip++]) << 3;
                t = (t >> 5) - 1;
            } else if (t >= 32) {  // M3
                t &= 31;
                if (t == 0) {
                    while (ip < inLen && in[ip] == 0) {
                        t += 255;
                        ++ip;
                    }
                    if (ip >= inLen) return fail("lzo: truncated M3 length");
                    t += 31 + in[ip++];
                }
                if (ip + 2 > inLen) return fail("lzo: truncated M3 distance");
                mPos = static_cast<int64_t>(op) - 1;
                mPos -= static_cast<int64_t>(in[ip] >> 2) + (static_cast<int64_t>(in[ip + 1]) << 6);
                ip += 2;
            } else if (t >= 16) {  // M4 (also holds the end-of-stream marker)
                mPos = static_cast<int64_t>(op) - (static_cast<int64_t>(t & 8) << 11);
                t &= 7;
                if (t == 0) {
                    while (ip < inLen && in[ip] == 0) {
                        t += 255;
                        ++ip;
                    }
                    if (ip >= inLen) return fail("lzo: truncated M4 length");
                    t += 7 + in[ip++];
                }
                if (ip + 2 > inLen) return fail("lzo: truncated M4 distance");
                mPos -= static_cast<int64_t>(in[ip] >> 2) + (static_cast<int64_t>(in[ip + 1]) << 6);
                ip += 2;
                if (mPos == static_cast<int64_t>(op)) {
                    outLen = op;
                    return true;  // end of stream
                }
                mPos -= static_cast<int64_t>(kM4ExtraOffset);
            } else {  // M1: two byte match
                if (ip + 1 > inLen) return fail("lzo: truncated M1 match");
                mPos = static_cast<int64_t>(op) - 1;
                mPos -= static_cast<int64_t>(t >> 2);
                mPos -= static_cast<int64_t>(in[ip++]) << 2;
                t = 0;
            }

            if (mPos < 0 || static_cast<uint64_t>(mPos) >= op) return fail("lzo: bad match distance");
            t += 2;
            if (op + t > outCap) return fail("lzo: output overrun");
            copyMatch(out + op, out + mPos, t);
            op += t;

        match_done:
            if (ip < 2) return fail("lzo: malformed stream");
            t = in[ip - 2] & 3;
            if (t == 0) break;  // leaves the inner loop, back to the main loop

        match_next:
            if (t == 0) return fail("lzo: zero length literal run");
            if (ip + t + 1 > inLen || op + t > outCap) return fail("lzo: overrun in trailing literals");
            std::memcpy(out + op, in + ip, t);
            op += t;
            ip += t;
            t = in[ip++];
            goto match;
        }
    }
}

bool lzo1xDecompressTo(const uint8_t* in, size_t inLen, size_t expectedSize, Bytes& out,
                       std::string* err) {
    size_t cap = expectedSize ? expectedSize : inLen * 4 + 1024;
    for (int attempt = 0; attempt < 8; ++attempt) {
        out.assign(cap, 0);
        size_t produced = 0;
        std::string localErr;
        if (lzo1xDecompress(in, inLen, out.data(), cap, produced, &localErr)) {
            out.resize(produced);
            return true;
        }
        if (expectedSize || localErr.find("output overrun") == std::string::npos) {
            if (err) *err = localErr;
            out.clear();
            return false;
        }
        cap *= 4;
    }
    if (err) *err = "lzo: output too large";
    out.clear();
    return false;
}

size_t lzo1xStoredBound(size_t inLen) { return inLen + inLen / 255 + 16; }

bool lzo1xStore(const uint8_t* in, size_t inLen, Bytes& out) {
    if (inLen == 0) return false;  // an empty stream is not representable
    out.clear();
    out.reserve(lzo1xStoredBound(inLen));

    if (inLen <= 238) {
        out.push_back(static_cast<uint8_t>(17 + inLen));
    } else {
        size_t tt = inLen - 18;
        out.push_back(0);
        while (tt > 255) {
            tt -= 255;
            out.push_back(0);
        }
        out.push_back(static_cast<uint8_t>(tt));
    }
    out.insert(out.end(), in, in + inLen);

    // End-of-stream marker: an M4 match whose distance resolves to the current
    // output position.
    out.push_back(0x11);
    out.push_back(0x00);
    out.push_back(0x00);
    return true;
}

}  // namespace m2
