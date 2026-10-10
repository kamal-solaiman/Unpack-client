// SPDX-License-Identifier: MIT
#include "unpacker.h"

#include <algorithm>
#include <cstdio>
#include <filesystem>
#include <functional>
#include <set>

#include "mapped_file.h"

namespace fs = std::filesystem;

namespace m2 {
namespace {

const char* const kPreferredExe[] = {"metin2client.exe", "metin2client.bin", "metin2.exe",
                                     "game.exe",     "client.exe",       "metin2client2.exe"};

std::string stemOf(const std::string& path) {
    return fs::path(path).stem().string();
}

int packSortRank(const std::string& name) {
    const std::string n = toLower(name);
    if (n == "root") return 0;
    if (n.rfind("locale", 0) == 0) return 1;
    if (n.rfind("map", 0) == 0) return 3;
    return 2;
}

std::vector<std::string> collectEixFiles(const fs::path& root, int maxDepth) {
    std::vector<std::string> out;
    std::error_code ec;
    std::function<void(const fs::path&, int)> walk = [&](const fs::path& dir, int depth) {
        if (depth > maxDepth) return;
        for (fs::directory_iterator it(dir, ec), end; !ec && it != end; it.increment(ec)) {
            const fs::path& p = it->path();
            if (it->status(ec).type() == fs::file_type::directory) {
                walk(p, depth + 1);
                continue;
            }
            if (toLower(p.extension().string()) == ".eix") out.push_back(p.string());
        }
    };
    walk(root, 0);
    std::sort(out.begin(), out.end());
    return out;
}

std::string jsonEscape(const std::string& s) {
    std::string out;
    for (char c : s) {
        switch (c) {
            case '"': out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default:
                if (static_cast<unsigned char>(c) < 0x20) {
                    char buf[8];
                    std::snprintf(buf, sizeof buf, "\\u%04x", c);
                    out += buf;
                } else {
                    out += c;
                }
        }
    }
    return out;
}

// Turns a KeyHit into a printable one liner.
std::string describeHit(const KeyHit& hit) {
    char buf[256];
    std::snprintf(buf, sizeof buf, "bytes: %s | dwords: %s | offset: 0x%llX | via %s",
                  hit.key.toByteHex().c_str(), hit.key.toHexArray().c_str(),
                  (unsigned long long)hit.fileOffset, hit.method.c_str());
    return buf;
}

}  // namespace

ClientFiles discoverClient(const std::string& path) {
    ClientFiles cf;
    std::error_code ec;
    fs::path p(path);
    if (!fs::exists(p, ec)) {
        Log::error("path does not exist: " + path);
        return cf;
    }
    cf.rootDir = fs::is_directory(p, ec) ? p.string() : p.parent_path().string();
    if (cf.rootDir.empty()) cf.rootDir = ".";

    // Look for the executable here and, when the user points the tool straight
    // at data/ or pack/, one level up.
    std::vector<std::string> searchDirs = {cf.rootDir};
    const fs::path parent = fs::path(cf.rootDir).parent_path();
    if (!parent.empty() && parent.string() != cf.rootDir) searchDirs.push_back(parent.string());

    for (const std::string& dir : searchDirs) {
        for (const char* name : kPreferredExe) {
            const std::string cand = joinPath(dir, name);
            if (fileExists(cand) &&
                std::find(cf.executables.begin(), cf.executables.end(), cand) == cf.executables.end())
                cf.executables.push_back(cand);
        }
    }
    for (const std::string& dir : searchDirs) {
        ec.clear();
        for (const auto& entry : fs::directory_iterator(dir, ec)) {
            if (!entry.is_regular_file(ec)) continue;
            const std::string ext = toLower(entry.path().extension().string());
            if (ext != ".exe" && ext != ".bin") continue;
            const std::string s = entry.path().string();
            if (std::find(cf.executables.begin(), cf.executables.end(), s) == cf.executables.end())
                cf.executables.push_back(s);
        }
        if (!cf.executables.empty()) break;  // prefer the closest directory
    }

    std::set<std::string> seenNames;
    for (const std::string& eix : collectEixFiles(cf.rootDir, 3)) {
        PackPair pair;
        pair.eix = eix;
        pair.name = stemOf(eix);
        const std::string epk = fs::path(eix).replace_extension(".epk").string();
        if (fileExists(epk)) pair.epk = epk;
        if (!seenNames.insert(pair.name).second) continue;  // keep the shallowest one
        cf.packs.push_back(std::move(pair));
    }
    std::stable_sort(cf.packs.begin(), cf.packs.end(), [](const PackPair& a, const PackPair& b) {
        const int ra = packSortRank(a.name), rb = packSortRank(b.name);
        if (ra != rb) return ra < rb;
        return a.name < b.name;
    });
    return cf;
}

std::string reportToJson(const std::vector<PackReport>& reports) {
    std::string out = "{\n  \"packs\": [\n";
    for (size_t r = 0; r < reports.size(); ++r) {
        const PackReport& rep = reports[r];
        out += "    {\n";
        out += "      \"name\": \"" + jsonEscape(rep.name) + "\",\n";
        out += "      \"eix\": \"" + jsonEscape(rep.eix) + "\",\n";
        out += "      \"epk\": \"" + jsonEscape(rep.epk) + "\",\n";
        out += "      \"ok\": " + std::string(rep.ok ? "true" : "false") + ",\n";
        if (!rep.error.empty()) out += "      \"error\": \"" + jsonEscape(rep.error) + "\",\n";
        out += "      \"indexEncrypted\": " + std::string(rep.indexEncrypted ? "true" : "false") + ",\n";
        out += "      \"indexKeyFound\": " + std::string(rep.indexKeyFound ? "true" : "false") + ",\n";
        out += "      \"dataKeyNeeded\": " + std::string(rep.dataKeyNeeded ? "true" : "false") + ",\n";
        out += "      \"dataKeyFound\": " + std::string(rep.dataKeyFound ? "true" : "false") + ",\n";
        if (rep.indexKeyFound) {
            out += "      \"indexKey\": {\"bytes\": \"" + rep.indexHit.key.toByteHex() + "\", \"dwords\": " +
                   rep.indexHit.key.toDwordArray() + ", \"offset\": " +
                   std::to_string(rep.indexHit.fileOffset) + ", \"method\": \"" +
                   jsonEscape(rep.indexHit.method) + "\"},\n";
        }
        if (rep.dataKeyFound) {
            out += "      \"dataKey\": {\"bytes\": \"" + rep.dataHit.key.toByteHex() + "\", \"dwords\": " +
                   rep.dataHit.key.toDwordArray() + ", \"offset\": " +
                   std::to_string(rep.dataHit.fileOffset) + ", \"method\": \"" +
                   jsonEscape(rep.dataHit.method) + "\"},\n";
        }
        out += "      \"entries\": " + std::to_string(rep.index.entries.size()) + ",\n";
        out += "      \"extracted\": " + std::to_string(rep.extracted) + ",\n";
        out += "      \"failed\": " + std::to_string(rep.failed) + ",\n";
        out += "      \"skipped\": " + std::to_string(rep.skipped) + ",\n";
        out += "      \"bytes\": " + std::to_string(rep.bytes) + ",\n";
        out += "      \"outputDir\": \"" + jsonEscape(rep.outputDir) + "\",\n";
        out += "      \"types\": {";
        bool first = true;
        for (const auto& kv : rep.typeHistogram) {
            if (!first) out += ", ";
            first = false;
            out += "\"" + jsonEscape(kv.first) + "\": " + std::to_string(kv.second);
        }
        out += "},\n";
        out += "      \"failures\": [";
        for (size_t i = 0; i < rep.failures.size() && i < 200; ++i) {
            if (i) out += ", ";
            out += "\n        {\"name\": \"" + jsonEscape(rep.failures[i].name) + "\", \"type\": " +
                   std::to_string(rep.failures[i].type) + ", \"error\": \"" +
                   jsonEscape(rep.failures[i].error) + "\"}";
        }
        out += rep.failures.empty() ? "]\n" : "\n      ]\n";
        out += std::string(r + 1 < reports.size() ? "    },\n" : "    }\n");
    }
    out += "  ]\n}\n";
    return out;
}

namespace {

struct KeyCache {
    bool loaded = false;
    Bytes image;
    PackKeys keys;
    KeySearchResult search;
    std::string exePath;
};

bool loadKeysForPack(const Bytes& eixRaw, const MappedFile& epk, const std::string& exePath,
                     const UnpackOptions& opt, KeyCache& cache, PackReport& rep) {
    if (!cache.loaded) {
        cache.loaded = true;
        cache.exePath = exePath;
        if (!opt.autoKeys && (opt.haveIndexKey || opt.haveDataKey)) {
            cache.keys.indexKey = opt.indexKey;
            cache.keys.haveIndexKey = opt.haveIndexKey;
            cache.keys.dataKey = opt.dataKey;
            cache.keys.haveDataKey = opt.haveDataKey;
            Log::verbose("using the keys supplied on the command line");
            return true;
        }
        if (exePath.empty() || !fileExists(exePath)) {
            Log::warn("no metin2client.exe found - cannot recover the keys automatically");
            cache.keys.indexKey = opt.indexKey;
            cache.keys.haveIndexKey = opt.haveIndexKey;
            cache.keys.dataKey = opt.dataKey;
            cache.keys.haveDataKey = opt.haveDataKey;
            if (!cache.keys.haveIndexKey && !cache.keys.haveDataKey) {
                // Last resort: the documented stock keys.
                size_t n = 0;
                const KnownKey* kk = knownKeys(n);
                for (int j = 0; j < 4; ++j) cache.keys.indexKey.w[j] = kk[0].w[j];
                for (int j = 0; j < 4; ++j) cache.keys.dataKey.w[j] = kk[1].w[j];
                cache.keys.haveIndexKey = cache.keys.haveDataKey = true;
                Log::verbose("falling back to the stock EterPack keys");
            }
            return true;
        }

        auto image = readFile(exePath);
        if (!image) {
            Log::error("cannot read " + exePath);
            return false;
        }
        cache.image = *image;
        Log::info("[*] scanning " + exePath + " (" + humanSize(cache.image.size()) + ") for XTEA keys...");

        KeyScanOptions scan;
        scan.includeKnown = true;
        scan.unaligned = opt.deepScan;
        scan.scanCode = true;
        scan.scanData = true;

        const uint8_t* epkData = epk.isOpen() ? epk.data() : nullptr;
        const size_t epkSize = epk.isOpen() ? epk.size() : 0;
        cache.search = searchKeys(cache.image, scan, eixRaw, epkData, epkSize,
                                  [](size_t done, size_t total, const std::string& stage) {
                                      if (stdoutIsTty() && Log::level >= LogLevel::Normal) {
                                          std::printf("\r[*] scanning for the %s key: %zu / %zu candidates   ",
                                                      stage.c_str(), done, total);
                                          std::fflush(stdout);
                                      } else {
                                          Log::debug("  key scan (" + stage + "): " + std::to_string(done) +
                                                     "/" + std::to_string(total));
                                      }
                                  });
        if (stdoutIsTty() && Log::level >= LogLevel::Normal) std::printf("\r%-78s\r", "");
        if (cache.search.indexKeyFound && cache.search.indexEncrypted) {
            cache.keys.indexKey = cache.search.indexHit.key;
            cache.keys.haveIndexKey = true;
            Log::info("[+] index key found  " + cache.search.indexHit.key.toHexArray());
            Log::verbose("    " + describeHit(cache.search.indexHit));
        } else if (!cache.search.indexEncrypted) {
            Log::info("[+] index is not XTEA encrypted");
        } else {
            Log::warn("index key NOT found");
        }
        if (cache.search.dataKeyFound) {
            cache.keys.dataKey = cache.search.dataHit.key;
            cache.keys.haveDataKey = true;
            Log::info("[+] data  key found  " + cache.search.dataHit.key.toHexArray());
            Log::verbose("    " + describeHit(cache.search.dataHit));
        } else if (cache.search.dataKeyNeeded) {
            Log::warn("data key NOT found");
        }

        // Manual keys always win over the scan.
        if (opt.haveIndexKey) {
            cache.keys.indexKey = opt.indexKey;
            cache.keys.haveIndexKey = true;
        }
        if (opt.haveDataKey) {
            cache.keys.dataKey = opt.dataKey;
            cache.keys.haveDataKey = true;
        }
        // Keep the stock keys as fallbacks for oddly labelled entries.
        size_t n = 0;
        const KnownKey* kk = knownKeys(n);
        for (size_t i = 0; i < n; ++i) {
            XteaKey k;
            for (int j = 0; j < 4; ++j) k.w[j] = kk[i].w[j];
            cache.keys.fallbacks.push_back(k);
        }
    }

    rep.indexEncrypted = cache.search.indexEncrypted;
    rep.indexKeyFound = cache.keys.haveIndexKey;
    rep.indexHit = cache.search.indexHit;
    rep.dataKeyNeeded = cache.search.dataKeyNeeded;
    rep.dataKeyFound = cache.keys.haveDataKey;
    rep.dataHit = cache.search.dataHit;
    return true;
}

int processPack(const PackPair& pack, const std::string& exePath, const UnpackOptions& opt,
                KeyCache& cache, PackReport& rep) {
    rep.name = pack.name;
    rep.eix = pack.eix;
    rep.epk = pack.epk;

    auto eixRaw = readFile(pack.eix);
    if (!eixRaw) {
        rep.error = "cannot read " + pack.eix;
        Log::error(rep.error);
        return 1;
    }
    MappedFile epk;
    if (!pack.epk.empty()) {
        std::string err;
        if (!epk.open(pack.epk, &err)) Log::warn(err + " (entries of type 0 may still work)");
    } else {
        Log::warn("no .epk next to " + pack.eix);
    }

    if (!loadKeysForPack(*eixRaw, epk, exePath, opt, cache, rep)) {
        rep.error = "key recovery failed";
        return 1;
    }

    std::string err;
    if (!loadIndexFile(*eixRaw, cache.keys, rep.index, &err)) {
        rep.error = err;
        Log::error(pack.name + ": " + err);
        if (exePath.empty())
            Log::warn("no client executable was found - point --exe at metin2client.exe, or pass "
                      "--index-key/--data-key manually");
        if (!cache.search.heuristic.empty() && !opt.json) {
            Log::warn("could not verify a key - best guesses from " + exePath + ":");
            size_t shown = 0;
            for (const KeyHit& h : cache.search.heuristic) {
                if (shown++ >= 8) break;
                Log::warn("    score " + std::to_string(h.score) + "  " + describeHit(h));
            }
            Log::warn("retry with: --index-key \"<bytes>\" (or --deep for an exhaustive scan)");
        }
        return 1;
    }

    Log::info("[*] " + pack.name + ": " + std::to_string(rep.index.entries.size()) + " entries, layout " +
              (rep.index.layout ? rep.index.layout->name : "?") + ", version " +
              std::to_string(rep.index.version));

    std::map<uint8_t, size_t> types;
    for (const PackEntry& e : rep.index.entries) types[e.type]++;
    for (const auto& kv : types) {
        rep.typeHistogram[packTypeName(static_cast<uint8_t>(kv.first))] = kv.second;
        Log::verbose("    type " + packTypeName(static_cast<uint8_t>(kv.first)) + ": " +
                     std::to_string(kv.second));
    }

    std::string outDir;
    if (opt.output.empty()) {
        outDir = joinPath("unpacked", pack.name);
    } else if (opt.multiPackOutput) {
        outDir = joinPath(opt.output, pack.name);
    } else {
        outDir = opt.output;
    }
    rep.outputDir = outDir;

    if (opt.listOnly) {
        if (!opt.json) {
            std::printf("%-16s %10s %10s %12s  %s\n", "type", "real size", "stored", "offset", "name");
            for (const PackEntry& e : rep.index.entries)
                std::printf("%-16s %10u %10u %12llu  %s\n", packTypeName(e.type).c_str(), e.realSize,
                            e.dataSize, (unsigned long long)e.offset, e.name.c_str());
        }
        rep.ok = true;
        rep.extracted = rep.index.entries.size();
        return 0;
    }

    if (!epk.isOpen()) {
        rep.error = "cannot read " + (pack.epk.empty() ? std::string("the .epk of ") + pack.name : pack.epk);
        Log::error(rep.error);
        return 1;
    }
    if (pack.epk.empty()) {
        rep.error = "no .epk file for " + pack.name;
        Log::error(rep.error);
        return 1;
    }
    if (!makeDirectories(outDir)) {
        rep.error = "cannot create output directory " + outDir;
        Log::error(rep.error);
        return 1;
    }

    const size_t total = rep.index.entries.size();
    size_t done = 0;
    std::set<std::string> written;
    for (const PackEntry& e : rep.index.entries) {
        ++done;
        if (!packTypeSupported(e.type) && !opt.autoTypes) {
            ++rep.skipped;
            FileResult fr;
            fr.name = e.name;
            fr.type = e.type;
            fr.error = "unsupported type " + packTypeName(e.type);
            rep.failures.push_back(fr);
            continue;
        }

        Bytes data;
        ExtractInfo info;
        std::string extractErr;
        const bool ok = extractEntry(epk.data(), epk.size(), e, cache.keys, opt.autoTypes, data, info,
                                     &extractErr);
        if (!ok) {
            if (!packTypeSupported(e.type)) ++rep.skipped;
            else ++rep.failed;
            FileResult fr;
            fr.name = e.name;
            fr.type = e.type;
            fr.error = extractErr;
            rep.failures.push_back(fr);
            Log::verbose("    [fail] " + e.name + ": " + extractErr);
            continue;
        }
        if (info.crcChecked && !info.crcOk && opt.verifyCrc)
            Log::verbose("    [warn] " + e.name + ": CRC mismatch after decode");

        std::string safe = e.safePath.empty() ? ("unnamed/" + std::to_string(e.id)) : e.safePath;
        if (!written.insert(toLower(safe)).second) {
            // Two entries map to the same file: keep both instead of silently
            // overwriting one of them.
            const size_t dot = safe.find_last_of('.');
            const std::string suffix = "#" + std::to_string(e.id);
            safe = (dot == std::string::npos) ? safe + suffix
                                              : safe.substr(0, dot) + suffix + safe.substr(dot);
            Log::warn("duplicate path in the index, saved as " + safe);
        }
        const std::string target = joinPath(outDir, safe);
        if (!writeFile(target, data)) {
            ++rep.failed;
            FileResult fr;
            fr.name = e.name;
            fr.type = e.type;
            fr.error = "cannot write " + target;
            rep.failures.push_back(fr);
            continue;
        }
        ++rep.extracted;
        rep.bytes += data.size();
        if (Log::level >= LogLevel::Verbose || (done % 500 == 0))
            Log::verbose("    [" + std::to_string(done) + "/" + std::to_string(total) + "] " + safe +
                         " (" + humanSize(data.size()) + ", " + info.method + ")");
    }

    rep.ok = rep.failed == 0;
    return rep.failed == 0 ? 0 : 1;
}

}  // namespace

int runUnpack(const UnpackOptions& opt) {
    std::error_code ec;
    fs::path input(opt.input);
    if (!fs::exists(input, ec)) {
        Log::error("no such file or directory: " + opt.input);
        return 2;
    }

    ClientFiles client;
    std::vector<PackPair> packs;
    std::string exePath = opt.exe;

    if (fs::is_regular_file(input, ec)) {
        const std::string ext = toLower(input.extension().string());
        PackPair pair;
        if (ext == ".eix") {
            pair.eix = input.string();
            pair.name = stemOf(pair.eix);
            const std::string epk = fs::path(pair.eix).replace_extension(".epk").string();
            if (fileExists(epk)) pair.epk = epk;
        } else if (ext == ".epk") {
            const std::string eix = fs::path(input).replace_extension(".eix").string();
            if (!fileExists(eix)) {
                Log::error("cannot find the index file: " + eix);
                return 2;
            }
            pair.eix = eix;
            pair.epk = input.string();
            pair.name = stemOf(eix);
        } else {
            // Maybe a base name without extension.
            const std::string eix = opt.input + ".eix";
            if (!fileExists(eix)) {
                Log::error("unsupported input file: " + opt.input);
                return 2;
            }
            pair.eix = eix;
            pair.name = stemOf(eix);
            const std::string epk = opt.input + ".epk";
            if (fileExists(epk)) pair.epk = epk;
        }
        packs.push_back(pair);
        client = discoverClient(fs::path(pair.eix).parent_path().parent_path().string());
        if (client.packs.empty()) client = discoverClient(fs::path(pair.eix).parent_path().string());
    } else {
        client = discoverClient(opt.input);
        packs = client.packs;
    }

    if (!opt.packFilter.empty()) {
        std::vector<PackPair> filtered;
        for (const PackPair& p : packs) {
            for (const std::string& f : opt.packFilter) {
                std::string want = toLower(f);
                if (want.size() > 4 && want.rfind(".eix") == want.size() - 4) want = want.substr(0, want.size() - 4);
                if (toLower(p.name) == want) {
                    filtered.push_back(p);
                    break;
                }
            }
        }
        if (filtered.empty()) {
            Log::error("no pack matches the filter (-p). Available:");
            for (const PackPair& p : packs) Log::error("    " + p.name);
            return 2;
        }
        packs = std::move(filtered);
    }

    if (packs.empty()) {
        Log::error("no .eix files found under " + opt.input);
        return 2;
    }
    if (exePath.empty() && !client.executables.empty()) exePath = client.executables.front();
    if (!exePath.empty()) Log::verbose("[*] client executable: " + exePath);
    if (client.executables.size() > 1) {
        for (size_t i = 1; i < client.executables.size(); ++i)
            Log::debug("other executable: " + client.executables[i]);
    }

    UnpackOptions effective = opt;
    effective.multiPackOutput = packs.size() > 1;

    KeyCache cache;
    std::vector<PackReport> reports;
    int worst = 0;
    for (const PackPair& pack : packs) {
        Log::info("=== " + pack.name + " ===");
        PackReport rep;
        const int rc = processPack(pack, exePath, effective, cache, rep);
        worst = std::max(worst, rc);
        reports.push_back(std::move(rep));
    }

    if (opt.json) {
        std::printf("%s", reportToJson(reports).c_str());
        return worst;
    }

    std::printf("\n---------------- summary ----------------\n");
    for (const PackReport& rep : reports) {
        std::printf("%-16s entries=%-6zu extracted=%-6zu failed=%-4zu skipped=%-4zu %s\n",
                    rep.name.c_str(), rep.index.entries.size(), rep.extracted, rep.failed, rep.skipped,
                    rep.ok ? "OK" : ("ERROR: " + rep.error).c_str());
        if (!rep.outputDir.empty() && !opt.listOnly && rep.extracted)
            std::printf("%-16s -> %s (%s)\n", "", rep.outputDir.c_str(), humanSize(rep.bytes).c_str());
        if (!rep.failures.empty() && Log::level >= LogLevel::Normal) {
            size_t shown = 0;
            for (const FileResult& fr : rep.failures) {
                if (shown++ >= 10) {
                    std::printf("                 ... %zu more problems (use --json or -v)\n",
                                rep.failures.size() - shown + 1);
                    break;
                }
                std::printf("                 ! %s [%s]: %s\n", fr.name.c_str(),
                            packTypeName(fr.type).c_str(), fr.error.c_str());
            }
        }
    }
    if (cache.search.indexKeyFound || cache.search.dataKeyFound) {
        std::printf("\nkeys recovered from %s\n", cache.exePath.c_str());
        if (cache.search.indexKeyFound) std::printf("  index: %s\n", describeHit(cache.search.indexHit).c_str());
        if (cache.search.dataKeyFound) std::printf("  data : %s\n", describeHit(cache.search.dataHit).c_str());
    }
    return worst;
}

int runKeys(const std::string& exePath, const std::string& eixPath, const std::string& epkPath,
            bool deep, bool json) {
    auto image = readFile(exePath);
    if (!image) {
        Log::error("cannot read " + exePath);
        return 2;
    }
    Bytes eixRaw;
    if (!eixPath.empty()) {
        auto e = readFile(eixPath);
        if (!e) {
            Log::error("cannot read " + eixPath);
            return 2;
        }
        eixRaw = *e;
    }
    MappedFile epk;

    PeImage pe;
    std::string peErr;
    if (parsePe(image->data(), image->size(), pe, &peErr))
        Log::verbose("[*] " + exePath + ": " + pe.describe());
    else
        Log::warn("PE parse failed (" + peErr + ") - falling back to a raw file scan");

    KeyScanOptions scan;
    scan.includeKnown = true;
    scan.unaligned = deep;
    Log::info("[*] scanning " + exePath + " (" + humanSize(image->size()) + "), deep=" +
              (deep ? "yes" : "no"));

    KeySearchResult res;
    if (!epkPath.empty()) {
        std::string err;
        if (!epk.open(epkPath, &err)) Log::warn(err);
    }

    res = searchKeys(*image, scan, eixRaw, epk.isOpen() ? epk.data() : nullptr,
                     epk.isOpen() ? epk.size() : 0,
                     [json](size_t done, size_t total, const std::string& stage) {
                         if (json || !stdoutIsTty()) return;
                         std::printf("\r[*] %s key: %zu / %zu candidates          ", stage.c_str(), done,
                                     total);
                         std::fflush(stdout);
                     });
    if (stdoutIsTty() && !json) std::printf("\r%-78s\r", "");

    if (json) {
        std::string out = "{\n  \"exe\": \"" + jsonEscape(exePath) + "\",\n";
        out += "  \"candidates\": " + std::to_string(res.candidatesTried) + ",\n";
        out += "  \"indexEncrypted\": " + std::string(res.indexEncrypted ? "true" : "false") + ",\n";
        out += "  \"indexKey\": ";
        if (res.indexKeyFound)
            out += "{\"bytes\": \"" + res.indexHit.key.toByteHex() + "\", \"dwords\": " +
                   res.indexHit.key.toDwordArray() + ", \"offset\": " +
                   std::to_string(res.indexHit.fileOffset) + ", \"method\": \"" +
                   jsonEscape(res.indexHit.method) + "\"}";
        else out += "null";
        out += ",\n  \"dataKey\": ";
        if (res.dataKeyFound)
            out += "{\"bytes\": \"" + res.dataHit.key.toByteHex() + "\", \"dwords\": " +
                   res.dataHit.key.toDwordArray() + ", \"offset\": " +
                   std::to_string(res.dataHit.fileOffset) + ", \"method\": \"" +
                   jsonEscape(res.dataHit.method) + "\"}";
        else out += "null";
        out += ",\n  \"stockKeysPresent\": [";
        for (size_t i = 0; i < res.knownPresent.size(); ++i) {
            if (i) out += ", ";
            out += "\n    {\"offset\": " + std::to_string(res.knownPresent[i].fileOffset) + ", \"what\": \"" +
                   jsonEscape(res.knownPresent[i].method) + "\", \"bytes\": \"" +
                   res.knownPresent[i].key.toByteHex() + "\"}";
        }
        out += res.knownPresent.empty() ? "],\n" : "\n  ],\n";
        out += "  \"heuristic\": [";
        for (size_t i = 0; i < res.heuristic.size(); ++i) {
            if (i) out += ", ";
            out += "\n    {\"bytes\": \"" + res.heuristic[i].key.toByteHex() + "\", \"dwords\": " +
                   res.heuristic[i].key.toDwordArray() + ", \"offset\": " +
                   std::to_string(res.heuristic[i].fileOffset) + ", \"score\": " +
                   std::to_string(res.heuristic[i].score) + ", \"method\": \"" +
                   jsonEscape(res.heuristic[i].method) + "\"}";
        }
        out += res.heuristic.empty() ? "]\n}\n" : "\n  ]\n}\n";
        std::printf("%s", out.c_str());
        return (res.indexKeyFound || !res.indexEncrypted) ? 0 : 1;
    }

    std::printf("\n%s\n", res.message.c_str());
    if (!res.knownPresent.empty()) {
        std::printf("\nstock keys physically present in the image:\n");
        for (const KeyHit& h : res.knownPresent)
            std::printf("  0x%08llX  %s  (%s)\n", (unsigned long long)h.fileOffset,
                        h.key.toByteHex().c_str(), h.method.c_str());
    }
    if (!eixRaw.empty()) {
        std::printf("\nindex (%s):\n", eixPath.c_str());
        if (!res.indexEncrypted)
            std::printf("  not XTEA encrypted - no index key needed\n");
        else if (res.indexKeyFound)
            std::printf("  VERIFIED\n    bytes  : %s\n    dwords : %s\n    found  : offset 0x%llX via %s\n",
                        res.indexHit.key.toByteHex().c_str(), res.indexHit.key.toHexArray().c_str(),
                        (unsigned long long)res.indexHit.fileOffset, res.indexHit.method.c_str());
        else
            std::printf("  no key could be verified\n");
    } else {
        std::printf("\n(no .eix supplied - pass --eix to verify candidates instead of guessing)\n");
    }
    if (epk.isOpen()) {
        std::printf("\ncontent (%s):\n", epkPath.c_str());
        if (!res.dataKeyNeeded)
            std::printf("  no encrypted entries found - no data key needed\n");
        else if (res.dataKeyFound)
            std::printf("  VERIFIED\n    bytes  : %s\n    dwords : %s\n    found  : offset 0x%llX via %s\n",
                        res.dataHit.key.toByteHex().c_str(), res.dataHit.key.toHexArray().c_str(),
                        (unsigned long long)res.dataHit.fileOffset, res.dataHit.method.c_str());
        else
            std::printf("  no key could be verified\n");
    }
    if (!res.heuristic.empty()) {
        std::printf("\nunverified candidates worth trying (ranked):\n");
        for (const KeyHit& h : res.heuristic)
            std::printf("  score %3d  %s  offset 0x%08llX  (%s)\n", h.score, h.key.toByteHex().c_str(),
                        (unsigned long long)h.fileOffset, h.method.c_str());
    }
    return (res.indexKeyFound || !res.indexEncrypted) ? 0 : 1;
}

int runInfo(const std::string& path, const std::string& exePath, bool json, bool deep) {
    auto raw = readFile(path);
    if (!raw) {
        Log::error("cannot read " + path);
        return 2;
    }
    const std::string ext = toLower(fs::path(path).extension().string());
    if (ext != ".eix") {
        Log::error("info currently supports .eix files");
        return 2;
    }

    PackKeys keys;
    KeySearchResult search;
    std::string err;
    const uint32_t magic = raw->size() >= 4 ? rd32(raw->data()) : 0;

    if (magic != kMagicEPKD && !exePath.empty()) {
        auto image = readFile(exePath);
        if (image) {
            KeyScanOptions scan;
            scan.unaligned = deep;
            const std::string epk = fs::path(path).replace_extension(".epk").string();
            MappedFile epkFile;
            if (fileExists(epk)) epkFile.open(epk, nullptr);
            search = searchKeys(*image, scan, *raw, epkFile.isOpen() ? epkFile.data() : nullptr,
                                epkFile.isOpen() ? epkFile.size() : 0, nullptr);
            if (search.indexKeyFound) {
                keys.indexKey = search.indexHit.key;
                keys.haveIndexKey = true;
            }
            if (search.dataKeyFound) {
                keys.dataKey = search.dataHit.key;
                keys.haveDataKey = true;
            }
            size_t n = 0;
            const KnownKey* kk = knownKeys(n);
            for (size_t i = 0; i < n; ++i) {
                XteaKey k;
                for (int j = 0; j < 4; ++j) k.w[j] = kk[i].w[j];
                keys.fallbacks.push_back(k);
            }
        }
    }

    PackIndex idx;
    const bool ok = loadIndexFile(*raw, keys, idx, &err);
    if (json) {
        std::string out = "{\n  \"file\": \"" + jsonEscape(path) + "\",\n";
        out += "  \"containerMagic\": \"" + fourccName(magic) + "\",\n";
        out += "  \"size\": " + std::to_string(raw->size()) + ",\n";
        out += "  \"parsed\": " + std::string(ok ? "true" : "false") + ",\n";
        if (!ok) out += "  \"error\": \"" + jsonEscape(err) + "\",\n";
        out += "  \"version\": " + std::to_string(idx.version) + ",\n";
        out += "  \"layout\": \"" + std::string(idx.layout ? idx.layout->name : "") + "\",\n";
        out += "  \"entryCount\": " + std::to_string(idx.entries.size()) + ",\n";
        if (search.indexKeyFound)
            out += "  \"indexKey\": \"" + search.indexHit.key.toByteHex() + "\",\n";
        if (search.dataKeyFound) out += "  \"dataKey\": \"" + search.dataHit.key.toByteHex() + "\",\n";
        std::map<std::string, size_t> types;
        std::map<std::string, size_t> dirs;
        for (const PackEntry& e : idx.entries) {
            types[packTypeName(e.type)]++;
            const size_t slash = e.name.find_first_of("/\\");
            dirs[slash == std::string::npos ? "(root)" : e.name.substr(0, slash)]++;
        }
        out += "  \"types\": {";
        bool first = true;
        for (const auto& kv : types) {
            if (!first) out += ", ";
            first = false;
            out += "\"" + jsonEscape(kv.first) + "\": " + std::to_string(kv.second);
        }
        out += "},\n  \"topDirectories\": {";
        first = true;
        for (const auto& kv : dirs) {
            if (!first) out += ", ";
            first = false;
            out += "\"" + jsonEscape(kv.first) + "\": " + std::to_string(kv.second);
        }
        out += "}\n}\n";
        std::printf("%s", out.c_str());
        return ok ? 0 : 1;
    }

    std::printf("file        : %s (%s)\n", path.c_str(), humanSize(raw->size()).c_str());
    std::printf("container   : %s\n", fourccName(magic).c_str());
    if (raw->size() >= 16 && magic != kMagicEPKD) {
        CryptedObject co;
        if (parseCryptedObjectHeader(raw->data(), raw->size(), co, nullptr)) {
            std::printf("encrypted   : %s\n", co.encrypted() ? "yes (XTEA)" : "no");
            std::printf("sizes       : encrypt=%u compressed=%u real=%u\n", co.encryptSize,
                        co.compressedSize, co.realSize);
        }
    }
    if (search.indexKeyFound)
        std::printf("index key   : %s  (%s)\n", search.indexHit.key.toByteHex().c_str(),
                    search.indexHit.method.c_str());
    if (search.dataKeyFound)
        std::printf("data key    : %s  (%s)\n", search.dataHit.key.toByteHex().c_str(),
                    search.dataHit.method.c_str());
    if (!ok) {
        std::printf("parse error : %s\n", err.c_str());
        return 1;
    }
    std::printf("version     : %u\n", idx.version);
    std::printf("layout      : %s (stride %zu)\n", idx.layout ? idx.layout->name : "?",
                idx.layout ? idx.layout->stride : 0);
    std::printf("entries     : %zu\n", idx.entries.size());
    std::map<std::string, size_t> types, dirs;
    uint64_t totalReal = 0, totalStored = 0;
    for (const PackEntry& e : idx.entries) {
        types[packTypeName(e.type)]++;
        totalReal += e.realSize;
        totalStored += e.dataSize;
        const size_t slash = e.name.find_first_of("/\\");
        dirs[slash == std::string::npos ? "(root)" : e.name.substr(0, slash)]++;
    }
    std::printf("sizes       : stored %s -> real %s\n", humanSize(totalStored).c_str(),
                humanSize(totalReal).c_str());
    std::printf("types       :\n");
    for (const auto& kv : types) std::printf("   %-22s %zu\n", kv.first.c_str(), kv.second);
    std::printf("directories :\n");
    size_t shown = 0;
    for (const auto& kv : dirs) {
        if (shown++ >= 25) {
            std::printf("   ... %zu more\n", dirs.size() - shown + 1);
            break;
        }
        std::printf("   %-30s %zu\n", kv.first.c_str(), kv.second);
    }
    std::printf("first files :\n");
    for (size_t i = 0; i < idx.entries.size() && i < 15; ++i) {
        const PackEntry& e = idx.entries[i];
        std::printf("   %-8s %9u  %s\n", packTypeName(e.type).c_str(), e.realSize, e.name.c_str());
    }
    return 0;
}

}  // namespace m2
