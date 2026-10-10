// SPDX-License-Identifier: MIT
// High level operations: discover a client directory, recover its keys and
// unpack one or more EterPacks to disk.
#pragma once

#include <map>
#include <string>
#include <vector>

#include "eterpack.h"
#include "key_finder.h"
#include "util.h"

namespace m2 {

struct PackPair {
    std::string name;    // "root"
    std::string eix;     // full path
    std::string epk;     // full path (may be empty)
};

struct ClientFiles {
    std::string rootDir;
    std::vector<std::string> executables;  // best guess first
    std::vector<PackPair> packs;
};

ClientFiles discoverClient(const std::string& path);

struct UnpackOptions {
    std::string input;                    // .eix file, pack base name or directory
    std::string output;                   // output directory ("" = auto)
    std::string exe;                      // explicit metin2client.exe
    std::vector<std::string> packFilter;  // only these pack names ("" = all)
    XteaKey indexKey{}, dataKey{};
    bool haveIndexKey = false, haveDataKey = false;
    bool autoKeys = true;
    bool autoTypes = true;
    bool deepScan = false;
    bool listOnly = false;
    bool overwrite = true;
    bool json = false;
    bool verifyCrc = true;
    bool multiPackOutput = false;  // put every pack in its own subdirectory of `output`
};

struct FileResult {
    std::string name;
    std::string error;
    std::string method;
    uint8_t type = 0;
    uint64_t size = 0;
};

struct PackReport {
    std::string name, eix, epk;
    bool ok = false;
    std::string error;
    bool indexEncrypted = false;
    bool indexKeyFound = false;
    bool dataKeyNeeded = false;
    bool dataKeyFound = false;
    KeyHit indexHit, dataHit;
    PackIndex index;
    size_t extracted = 0, failed = 0, skipped = 0;
    uint64_t bytes = 0;
    std::vector<FileResult> failures;
    std::string outputDir;
    std::map<std::string, size_t> typeHistogram;
};

// Runs everything; returns a process exit code.
int runUnpack(const UnpackOptions& opt);
int runKeys(const std::string& exePath, const std::string& eixPath, const std::string& epkPath,
            bool deep, bool json);
int runInfo(const std::string& path, const std::string& exePath, bool json, bool deep);

std::string reportToJson(const std::vector<PackReport>& reports);

}  // namespace m2
