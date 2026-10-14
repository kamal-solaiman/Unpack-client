# History Unpacker

Standalone C++17 console tool for the **History** D2 archive profile supplied in this repository. All menus, commands, diagnostics and reports are in English. No Alt2 code, client execution, injection, Python runtime, network service or runtime DLL dependency is needed by the tool.

## What was actually verified

The checkout contains `History2.exe` and `pack/workplace.d2`; it does **not** contain a separate `pack/root` file. The supplied archive holds 813 entries. Every entry was decrypted, decompressed and verified successfully. The C++ extractor's complete output was also compared against an independent Python implementation with an aggregate SHA-256 test.

- AES-256-CFB128, reset to the same archive IV for each entry.
- Raw LZ4 blocks when stored and original sizes differ; otherwise uncompressed bytes.
- XXH32 content checksums with seed `0xF00FED5C`.
- CRC32 filename hashes after ASCII lowercase and backslash-to-slash normalization.
- The supplied archive's working AES key and IV are in its **archive header**. No executable key or XOR mask is needed for this sample. The executable is read only as a filename-reference source.

**No claim is made that arbitrary EXEs can be scanned for a universally valid encryption key.** The client loader supports optional XOR masks for other archives, but that variant is not implemented here. Wrong keys/variants fail checksum validation and are not exported as successful files.

## Build with Visual Studio 2026

Install Visual Studio 2026 with **Desktop development with C++**, the Windows SDK and **C++ CMake tools for Windows**. The `Visual Studio 18 2026` CMake generator requires **CMake 4.2 or newer**. If Visual Studio's bundled CMake is older, install a newer CMake and make sure it is the one on your `PATH` when running the build script.

### Open Folder

1. Visual Studio 2026 → **File → Open → Folder** → select `History/HistoryUnpacker`.
2. Allow CMake to configure; select an x64 Release configuration.
3. Build target `HistoryUnpacker` and run it. With no command it opens the menu.

### Generate a solution

From a Visual Studio 2026 Developer Command Prompt, run `build-vs.bat`, or:

```bat
cd History\HistoryUnpacker
cmake -S . -B build -G "Visual Studio 18 2026" -A x64
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
build\Release\HistoryUnpacker.exe
```

CMake generates `build/HistoryUnpacker.sln`. All C/C++ dependencies and their licenses are vendored. Compilation does not download anything. Python is optional, used only for the additional integration test when installed.

Copy the EXE **and its `data` directory** when moving the tool elsewhere. Use `--archive` and `--exe` outside this checkout. The tool searches up to seven parent directories for the supplied History assets as a convenience.

Linux development build: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure`.

The implementation was compiled/tested on Linux in this session; Visual Studio build files are supplied, but an actual Windows/MSVC run was not available.

## Menu

1. Inspect archive.
2. Extract and validate the archive key / IV (displayed, not saved automatically).
3. Recover and list filenames.
4. Decrypt one file by original virtual name.
5. Decrypt all files.
6. Verify all payloads without writing files.
7. Export filename/metadata CSV.
8. Change archive and output paths.
9. Set History EXE and additional filename dictionary.
10. Toggle export of unresolved names.
0. Exit.

Errors return to the menu. Console input and Windows command-line paths use UTF-8/Unicode. The archive profile's filename hash normalization is ASCII; non-ASCII original filename encodings have not been established from this sample.

## Command examples

From the repository root, replacing `HistoryUnpacker` with the path to your compiled EXE:

```bat
HistoryUnpacker --archive "History\pack\workplace.d2" info
HistoryUnpacker --archive "History\pack\workplace.d2" keys
HistoryUnpacker --archive "History\pack\workplace.d2" verify
HistoryUnpacker --archive "History\pack\workplace.d2" --exe "History\History2.exe" list
HistoryUnpacker --out "History\unpacked\single" extract "ui.py"
HistoryUnpacker --out "History\unpacked\resolved" all
HistoryUnpacker --out "History\unpacked\complete" --include-unresolved all
HistoryUnpacker --names "my-names.txt" manifest "names-report.csv"
```

To try a separately supplied `pack/root`, use `--archive "path\to\pack\root"`. Extension does not matter; its **format must match**. Other formats are explicitly rejected rather than guessed.

Exit codes: **0** success; **1** failure (possibly partial extraction); **2** extraction completed but unresolved files were skipped. Inspect `history-manifest.csv` for per-entry status.

## Original names and extensions: important limitations

This format does **not** store encrypted filenames or a reversible filename table. It stores only 32-bit CRC32 identifiers. A hash cannot uniquely reconstruct its input. Therefore a guarantee of restoring every exact original name would be misleading.

The tool:

- Loads a bundled list of 569 normalized candidate paths recovered from this History EXE and the verified payloads.
- Scans executable strings, UTF-16 references, decoded file references and Python module identifiers.
- Accepts candidates only when their normalized CRC32 equals an entry's identifier.
- Rejects an automatic name when multiple distinct candidates match the same identifier.
- Accepts additional paths via `--names` (one path per line; `#` starts a comment).
- Lets `extract NAME` look up a supplied name directly, even if it was not in any dictionary.

With the supplied executable and current scanner, **568 of 813 entries have a unique recovered candidate**. The other **245 are unresolved or ambiguous**, including one hash with multiple candidates. CRC equality itself is not a mathematical proof of the original name, and original letter casing is not recoverable because the client lowercases before hashing.

Resolved files retain the recovered original extension and directory hierarchy. Extraction is **binary and type-agnostic**: DDS, TGA, GR2, MSE, MSM, XML, audio, scripts and any other bytes follow the same path; there is no PY/TXT-only filter. This does not convert proprietary formats into standard ones, and not every named format is necessarily present in this sample.

Unknown names are skipped by default. Opting in exports them as `_unresolved/<crc32>.unresolved`, **not fake `.bin`, `.py` or guessed media extensions**. These files have fully verified original contents, but their names remain unknown. The CSV explicitly records that distinction. Supply more original path candidates and extract into a fresh directory to recover additional names.

Virtual game paths such as `d:/ymir work/...` become relative `d/ymir work/...` directories; the original candidate is retained in the manifest.

## Safety and limits

- Input archives and executable are read-only. No executable is launched.
- Every payload must decrypt/decompress and pass its checksum before it is written.
- XXH32 is a corruption/wrong-key check, **not cryptographic authentication**.
- Existing files are never overwritten; use a fresh output directory for each complete extraction.
- Full extraction writes `history-manifest.csv`, including per-file failures and unresolved status.
- Traversal, absolute/UNC paths, Windows device names, alternate streams, unsafe suffixes and existing redirected output directories are rejected.
- Do not extract into a directory concurrently modified by an untrusted process; filesystem checks cannot eliminate all directory-race attacks.
- Archive size is limited to the format's 32-bit offsets (under 4 GiB). Each stored/decoded entry is limited to 256 MiB; at most one million entries are allowed. Payloads are processed one at a time.
- A changed or corrupt input, unsupported masks/profile, unwritable destination, duplicate hash, malformed offsets, truncated data, invalid LZ4 and checksum mismatch produce explicit errors.

## Tests and source layout

- `src/history.*`: bounded archive parsing, AES-CFB, LZ4, checksums, candidate recovery and safe output.
- `src/main.cpp`: menu, CLI, reporting and Unicode Windows entry point.
- `tests/tests.cpp`: NIST AES-256-CFB128 vectors, partial blocks, CRC32, LZ4 overlap and invalid streams, invalid archives, unsafe paths and overwrite protection.
- `tests/integration.py`: optional stdlib-only test of all 813 fixture entries, independent aggregate digest, single extraction, unresolved policy, corruption and malformed metadata.
- `FORMAT.md`: on-disk layout and client analysis notes.
- `third_party/SOURCES.txt`: pinned third-party revisions and licenses.

Use only with client assets you own or are authorized to analyze.
