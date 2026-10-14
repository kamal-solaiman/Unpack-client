# History Unpacker

Standalone C++17 console tool for the **History** D2 archive profile supplied in this repository. All menus, commands, diagnostics and reports are in English. No Alt2 code, client execution, injection, Python runtime, network service or runtime DLL dependency is needed by the tool.

The tool is **not limited to `workplace.d2`**. It processes every History D2 archive you point it at: pass a directory and it discovers all archives inside (recursively, `pack\` first), pass `--archive` several times to pick individual files, or pass nothing and it searches the working directory and its parents. Every command - `info`, `keys`, `list`, `verify`, `extract`, `all`, `manifest` - runs over the whole selection.

## What was actually verified

The checkout contains `History2.exe` and `pack/workplace.d2`; it does **not** contain a separate `pack/root` file. The supplied archive holds 813 entries. Every entry was decrypted, decompressed and verified successfully. The C++ extractor's complete output was also compared against an independent Python implementation with an aggregate SHA-256 test.

A client `pack` directory normally holds several archives (`workplace.d2`, `locale_*.d2`, `root`, ...). Point the tool at that directory and all of them are found by their `0xF00FED5C` magic - the file extension is never trusted, and files that only look like archives are reported as rejected instead of guessed at.

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

Discovery limits: a directory argument is searched up to four levels deep, the automatic
parent search goes up seven levels and stops at the first level that yields archives, and
`--archive` can be repeated as often as needed to select archives beyond those limits.

## Menu

The menu header lists every archive currently selected (the first eight, plus a count of the rest).

1. Inspect archives.
2. Extract and validate the archive key / IV of each archive (displayed, not saved automatically).
3. Scan the selected directories for archives and report which ones are usable.
4. Recover and list filenames.
5. Decrypt one file by original virtual name (searched in every selected archive).
6. Decrypt all files of every selected archive.
7. Verify all payloads without writing files.
8. Export filename/metadata CSV.
9. Change archive (file, directory or `;`-separated list) and output paths.
10. Set History EXE and additional filename dictionaries (`;`-separated).
11. Toggle export of unresolved names.
0. Exit.

Errors return to the menu. Console input and Windows command-line paths use UTF-8/Unicode. The archive profile's filename hash normalization is ASCII; non-ASCII original filename encodings have not been established from this sample.

## Command examples

From the repository root, replacing `HistoryUnpacker` with the path to your compiled EXE:

```bat
HistoryUnpacker --archive "History\pack\workplace.d2" info
HistoryUnpacker --archive "History\pack\workplace.d2" keys
HistoryUnpacker --archive "C:\Metin2\pack" scan
HistoryUnpacker --archive "C:\Metin2\pack" verify
HistoryUnpacker --archive "C:\Metin2\pack" --exe "C:\Metin2\History2.exe" list
HistoryUnpacker --archive "C:\Metin2\pack" --out "C:\unpacked\resolved" all
HistoryUnpacker --archive "C:\Metin2\pack" --out "C:\unpacked\complete" --include-unresolved all
HistoryUnpacker --archive "pack\workplace.d2" --archive "pack\locale_sound.d2" --out "out\two" all
HistoryUnpacker --out "History\unpacked\single" extract "ui.py"
HistoryUnpacker --names "my-names.txt" manifest "names-report.csv"
```

`--archive` accepts a **file or a directory** and may be repeated. A directory is searched
recursively (up to four levels, `pack\` first) and every file whose first four bytes are the
D2 magic is selected; `workplace.d2` is ordered first for familiarity. Extension does not
matter, so a separately supplied `pack/root` works with `--archive "path\to\pack\root"`.
Other formats - including Alt2 `root` (`0x000FED0C`) - are explicitly rejected rather than
guessed, and a directory that contains no D2 archive is an error, not an empty success.

### Output layout with several archives

Each archive is extracted into its own subfolder of `--out`, named after the archive file
(`workplace.d2` -> `out\workplace\`), so identical filenames in different archives never
collide:

```
out\
  history-manifest-all.csv     combined report (archive, output_folder, per-entry status)
  workplace\
    history-manifest.csv       per-archive report
    ui.py, uiscript\..., _unresolved\...
  locale_sound\
    history-manifest.csv
    ...
```

`extract NAME` still writes directly into `--out` (no subfolder) and searches the archives in
order, reporting which archive supplied the file. `manifest FILE.csv` writes exactly the one
requested CSV - with `archive` and `output_folder` columns - and no payload. A single archive
behaves the same way, it simply produces one subfolder.

Exit codes: **0** success; **1** failure (possibly partial extraction, or at least one archive was rejected/unusable); **2** extraction completed but unresolved files were skipped. Inspect `history-manifest.csv` (per archive) or `history-manifest-all.csv` (whole selection) for per-entry status.

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
- In a batch, one rejected or corrupt archive never aborts the others: it is reported with its reason, the remaining archives are processed, and the exit code reflects the failure.

## Tests and source layout

- `src/history.*`: bounded archive parsing, AES-CFB, LZ4, checksums, candidate recovery, archive discovery and safe output.
- `src/main.cpp`: menu, CLI, per-archive batch processing, reporting and Unicode Windows entry point.
- `tests/tests.cpp`: NIST AES-256-CFB128 vectors, partial blocks, CRC32, LZ4 overlap and invalid streams, invalid archives, unsafe paths, overwrite protection and archive discovery (magic sniffing, name filter, directory expansion, parent search).
- `tests/integration.py`: optional stdlib-only test of all 813 fixture entries, independent aggregate digest, single extraction, unresolved policy, corruption and malformed metadata, plus multi-archive discovery, batch extraction into per-archive folders and the combined manifest.
- `FORMAT.md`: on-disk layout and client analysis notes.
- `third_party/SOURCES.txt`: pinned third-party revisions and licenses.

Use only with client assets you own or are authorized to analyze.
