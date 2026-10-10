// SPDX-License-Identifier: MIT
// unpack-client - Metin2 EterPack (.eix/.epk) decryptor & unpacker with
// automatic XTEA key recovery from metin2client.exe.
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "selftest.h"
#include "unpacker.h"
#include "util.h"

using namespace m2;

namespace {

void printUsage() {
    std::printf(
        "unpack-client - Metin2 data/root (.eix/.epk) decryptor & unpacker\n"
        "\n"
        "USAGE\n"
        "  unpack-client unpack <client-dir | data/root | root.eix> [options]\n"
        "  unpack-client keys   <metin2client.exe> [--eix root.eix] [--epk root.epk]\n"
        "  unpack-client info   <root.eix> [--exe metin2client.exe]\n"
        "  unpack-client test\n"
        "\n"
        "EXAMPLES\n"
        "  unpack-client unpack D:/Metin2 -p root            # unpack data/root only\n"
        "  unpack-client unpack D:/Metin2/data/root.eix -o D:/out/root\n"
        "  unpack-client keys D:/Metin2/metin2client.exe --eix D:/Metin2/data/root.eix\n"
        "  unpack-client unpack . --index-key \"b9 9e b0 02 ...\" --data-key \"22 b8 ...\"\n"
        "\n"
        "OPTIONS\n"
        "  -o, --out DIR        output directory (default: ./unpacked/<pack>)\n"
        "  -e, --exe FILE       client executable to recover the keys from\n"
        "  -p, --pack NAME      only this pack (repeatable; 'root', 'locale_europe'...)\n"
        "      --index-key K    XTEA key of the .eix  (16 hex bytes or 4 dwords)\n"
        "      --data-key  K    XTEA key of the .epk entries\n"
        "      --eix FILE       (keys/info) index file used to verify candidates\n"
        "      --epk FILE       (keys) content file used to verify the data key\n"
        "      --no-auto-keys   do not scan the executable, use only the given keys\n"
        "      --strict-types   trust the type byte instead of auto detecting\n"
        "      --deep           exhaustive scan (unaligned + permutations), slower\n"
        "      --list           list entries, do not write any file\n"
        "      --json           machine readable report\n"
        "      --no-crc         do not verify the stored CRC32\n"
        "  -v, --verbose        more output\n"
        "      --debug          even more output\n"
        "  -q, --quiet          warnings and errors only\n"
        "  -h, --help           this text\n");
}

struct Args {
    std::string command;
    std::vector<std::string> positional;
    std::string out, exe, eix, epk, indexKey, dataKey;
    std::vector<std::string> packs;
    bool autoKeys = true, autoTypes = true, deep = false, list = false, json = false;
    bool verifyCrc = true;
    LogLevel level = LogLevel::Normal;
};

bool needsValue(int& i, int argc, char** argv, const std::string& flag, std::string& dest) {
    if (i + 1 >= argc) {
        Log::error(flag + " needs a value");
        return false;
    }
    dest = argv[++i];
    return true;
}

}  // namespace

int main(int argc, char** argv) {
    Args a;
    for (int i = 1; i < argc; ++i) {
        const std::string s = argv[i];
        if (s == "-h" || s == "--help") {
            printUsage();
            return 0;
        } else if (s == "-v" || s == "--verbose") {
            a.level = LogLevel::Verbose;
        } else if (s == "--debug") {
            a.level = LogLevel::Debug;
        } else if (s == "-q" || s == "--quiet") {
            a.level = LogLevel::Quiet;
        } else if (s == "-o" || s == "--out") {
            if (!needsValue(i, argc, argv, s, a.out)) return 2;
        } else if (s == "-e" || s == "--exe") {
            if (!needsValue(i, argc, argv, s, a.exe)) return 2;
        } else if (s == "-p" || s == "--pack") {
            std::string v;
            if (!needsValue(i, argc, argv, s, v)) return 2;
            a.packs.push_back(v);
        } else if (s == "--index-key") {
            if (!needsValue(i, argc, argv, s, a.indexKey)) return 2;
        } else if (s == "--data-key") {
            if (!needsValue(i, argc, argv, s, a.dataKey)) return 2;
        } else if (s == "--eix") {
            if (!needsValue(i, argc, argv, s, a.eix)) return 2;
        } else if (s == "--epk") {
            if (!needsValue(i, argc, argv, s, a.epk)) return 2;
        } else if (s == "--no-auto-keys") {
            a.autoKeys = false;
        } else if (s == "--strict-types") {
            a.autoTypes = false;
        } else if (s == "--deep") {
            a.deep = true;
        } else if (s == "--list") {
            a.list = true;
        } else if (s == "--json") {
            a.json = true;
            a.level = LogLevel::Quiet;
        } else if (s == "--no-crc") {
            a.verifyCrc = false;
        } else if (!s.empty() && s[0] == '-') {
            Log::error("unknown option: " + s);
            return 2;
        } else {
            a.positional.push_back(s);
        }
    }
    Log::level = a.level;

    size_t pos = 0;
    const std::vector<std::string> cmds = {"unpack", "keys", "info", "test", "help"};
    if (!a.positional.empty()) {
        for (const std::string& c : cmds) {
            if (toLower(a.positional[0]) == c) {
                a.command = c;
                pos = 1;
                break;
            }
        }
    }
    if (a.command.empty()) a.command = "unpack";

    if (a.command == "help") {
        printUsage();
        return 0;
    }
    if (a.command == "test") return runSelfTests(a.level >= LogLevel::Verbose);

    if (a.command == "keys") {
        std::string exe = pos < a.positional.size() ? a.positional[pos] : a.exe;
        if (exe.empty()) {
            Log::error("keys needs the client executable, e.g.: unpack-client keys metin2client.exe");
            return 2;
        }
        return runKeys(exe, a.eix, a.epk, a.deep, a.json);
    }

    if (a.command == "info") {
        std::string target = pos < a.positional.size() ? a.positional[pos] : a.eix;
        if (target.empty()) {
            Log::error("info needs an .eix file");
            return 2;
        }
        return runInfo(target, a.exe, a.json, a.deep);
    }

    UnpackOptions opt;
    opt.input = pos < a.positional.size() ? a.positional[pos] : std::string(".");
    opt.output = a.out;
    opt.exe = a.exe;
    opt.packFilter = a.packs;
    opt.autoKeys = a.autoKeys;
    opt.autoTypes = a.autoTypes;
    opt.deepScan = a.deep;
    opt.listOnly = a.list;
    opt.json = a.json;
    opt.verifyCrc = a.verifyCrc;
    if (!a.indexKey.empty()) {
        auto k = XteaKey::parse(a.indexKey);
        if (!k) {
            Log::error("cannot parse --index-key (use 16 hex bytes or 4 dwords)");
            return 2;
        }
        opt.indexKey = *k;
        opt.haveIndexKey = true;
    }
    if (!a.dataKey.empty()) {
        auto k = XteaKey::parse(a.dataKey);
        if (!k) {
            Log::error("cannot parse --data-key (use 16 hex bytes or 4 dwords)");
            return 2;
        }
        opt.dataKey = *k;
        opt.haveDataKey = true;
    }
    if (opt.listOnly && opt.output.empty()) opt.output = "unpacked";
    return runUnpack(opt);
}
