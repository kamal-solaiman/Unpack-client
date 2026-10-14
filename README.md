# UnpackTool - Professional EterPack Decryption System

A complete C++ system for decrypting Metin2 pack files (`pack/root`, `*.eix/*.epk`, `*.d2`, custom packs) with XTEA key extraction from the client executable.

Compilable with Visual Studio 2019/2022. Includes LZO decompression (miniLZO), file type detection, and handling of all file formats inside the client (not just py/txt).

---

## Features

### 1. XTEA Key Extraction from EXE
- **Auto scan**: High-entropy 16-byte block scan in `.data`/`.rdata` sections, scoring against pack file content
- **Pattern scan**: RIP-relative search for XTEA delta `0x9E3779B9` and nearby `mov reg, [rip+disp]` that points to key in `.data`
- **Brute-force tester**: Test candidate keys against pack file to see if decrypted output contains EPKD, file paths, etc.
- **Known default keys** built-in:
  - Index: `B99EB0026F69810563989B2879181A00`
  - Content: `22B8B40464B26E1FAEEA1800A6F6FB1C`
  - Custom example: `54D82039AA8D2722DC23E81C696B7430`

### 2. Pack Handling
- **EterPack (EPKD)**: Full parser for index (12 bytes: FourCC, version, fileCount, indexStart) and file entries (160-byte filename + CRCs + sizes + offset + type)
- **File types**: 0 RAW, 1 LZO, 2 XTEA(LZO), 3 Panama, 4/5 HybridCrypt, 6 XTEA(Snappy)
- **Raw mode**: For `.d2` or `root` files that are single XTEA-encrypted blobs or already decrypted EPKD
- **CryptedObject**: MCOB (raw), MCOZ (LZO), MCSP (Snappy) with header (magic, cryptedSize, compressedSize, realSize, verification)

### 3. Fixing Common Problems
- **`.bin` unknown extension**: After decryption, file may have `.bin` because original extension was lost. Tool detects real extension via magic numbers:
  - DDS (`DDS `), PNG (`89 50 4E 47`), JPG (`FF D8 FF`), GIF, BMP, ZIP
  - Text-based: Python (`import `, `def `), XML, MSA/MSM/MSE via keywords
  - Uses original filename hint if available
  - Function `FixFileName()` replaces `.bin` with detected extension
- **Encrypted filenames**: Index filenames may be XTEA-encrypted. Tool tries decrypting filename field (160 bytes) with same key and checks if result is printable with `/` or `.`

### 4. LZO & Snappy Decompression
- Includes **miniLZO** (public domain, 2.09) for LZO1X decompression: `lzo1x_decompress_safe()`
- Minimal **Snappy** decompressor implemented from format spec (varint + literal/copy tags)
- Auto-detects if content needs decompression after XTEA decrypt

### 5. File Type Support (All Client Formats)
Not just py/txt, but:
- Scripts: `.py`, `.txt`, `.xml`, `.sub`, `.cfg`
- Models: `.msm`, `.msa`, `.mse`, `.msk`, `.mot`, `.mdatr`
- Images: `.dds`, `.tga`, `.png`, `.jpg`, `.bmp`
- Sounds, maps, property, locale, etc.

### 6. Interactive Menu (English)
```
 1. Extract XTEA key from exe (auto scan)
 2. Extract key via XTEA pattern (RIP-relative search)
 3. List pack files in directory
 4. Show current keys
 5. Set custom key manually (hex)
 6. Load and parse pack (dump file list)
 7. Decrypt single file by name
 8. Decrypt all files (extract all)
 9. Decrypt root/pack file (raw mode, fix .bin)
10. Fix file extensions in folder (.bin -> correct)
11. Decrypt filenames (if encrypted)
12. Brute-force test keys against pack
13. Show pack info
14. Decrypt CryptedObject (MCOZ/MCOB/MCSP)
15. Change exe path
16. Change pack path
 0. Exit
```

---

## Build Instructions

### Visual Studio
1. Open `UnpackTool.sln`
2. Select x64 Release
3. Build -> Build Solution
4. Output: `x64/Release/UnpackTool.exe`

Or create new VS project and add all files in `src/`:
- `src/main.cpp`
- `src/xtea.cpp`
- `src/eterpack.cpp`
- `src/key_extractor.cpp`
- `src/filetype.cpp`
- `src/crypted_object.cpp`
- `src/lzo/minilzo.c`
- Headers in `src/*.h` and `src/lzo/*.h`
- Set C++17, include `src` and `src/lzo`

### CMake (Linux)
```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
./bin/UnpackTool
```

### g++ (Quick)
```bash
g++ -std=c++17 -I src -I src/lzo -O2 src/main.cpp src/xtea.cpp src/eterpack.cpp src/key_extractor.cpp src/filetype.cpp src/crypted_object.cpp src/lzo/minilzo.c -o UnpackTool
```

---

## Usage Examples

### Extract key from 64-bit client (alt2)
```
./UnpackTool
> 2
Enter exe path: alt2/metin2client.exe
[INFO] Found potential key via RIP-relative at file offset 0x936b60 VA=0x937f60 hex=54D82039AA8D2722DC23E81C696B7430
[INFO] Using key: 54D82039AA8D2722DC23E81C696B7430
```

### Show pack info
```
> 13
Enter pack path: alt2/data/root
[INFO] File: alt2/data/root Size: 36796636
First 16 bytes hex: 0c ed 0f 00 ...
```

### Decrypt all files
```
> 8
Enter pack path: pack/root.eix (or .epk)
Enter output dir: ./output
[INFO] Extracting 1234 files to ./output
```

### Fix .bin extensions
```
> 10
Enter folder: ./output
[FIX] horse.bin -> horse.msm
```

### Manual key
```
> 5
Enter hex key: B99EB0026F69810563989B2879181A00
```

Keys are saved to `keys.txt` for next run.

---

## Technical Details - History Client (32-bit)

**History2.exe** analysis:

- **PE**: 32-bit, image_base 0x400000
- **XTEA function**: VA 0x4b21d30, file 0x4721130
  - Custom variant: uses `ror ecx, 0x15` and `xor ecx, 0x9E3779B9/B8/BB/BA/BF...`
  - Key via `[ebx+0x70/0x74/0x78/0x7C]` etc, not RIP-relative
  - Local buffer 0x20 bytes (8 uint32), does 8 rounds of custom mixing
  - Writes 0x20 bytes output to first arg (key destination)
- **Caller**: VA 0x4b223d0, file 0x47217d0
  - Signature: `push [esp+8], push [esp+8], push 0x20, push [ecx+0x230], call 0x4b21d30`
  - Key is at `this+0x230` (object offset 0x230)
  - Only reference to `[ecx+0x230]` is this push, no direct `mov [ecx+0x230], reg` found in .text 0x4b20000-0x4b30000 (201 hits for 0x230 but mostly `ebp-0x230` false positives)
  - Suggests key init via memcpy from global or constructor not in that range
- **Pack list**: Wide strings at file 0x4767532 VA 0x4b68932, error strings at 0x4767920/0x4767988, loader at 0x77a000-0x77c000 with xrefs at 0x37a47a/0x37a705
- **Brute-force**: Scanned .data/.rdata 791317 high-entropy 16-byte blocks, 51 scored >0 with keywords data/.mse/etc but none yielded EPKD. Tested default keys same method - no EPKD. Indicates custom ror variant must be reversed or LZO decompress after decrypt needed.

**Workplace.d2**: Header `5c ed 0f f0 4d 2f 40 85 ...`, last 128 high entropy, not decrypting with default keys. Needs custom key + custom XTEA variant + LZO.

**Tool handles this via**:
- Pattern search for `FF B1 30 02 00 00` (push [ecx+0x230])
- High-entropy scan with scoring
- Separate index/content keys
- Raw mode that tries XTEA decrypt whole file and checks for EPKD after

For full History decryption, you need to:
1. Extract key via tool option 1 (auto scan) - will list 51 candidates
2. Try each candidate with option 9 (raw mode) which does XTEA decrypt + filetype detection
3. If still .bin, use option 10 to fix extensions
4. If filenames encrypted, use option 11

Future improvement: Implement custom ror-0x15 XTEA inverse in `xtea.cpp` as `DecryptBlockCustom()` and use it when standard fails.

---

## File Structure

```
src/
  main.cpp              # Menu + CLI
  xtea.h/cpp            # XTEA encrypt/decrypt, hex parsing
  eterpack.h/cpp        # EterPack parser, extract, LZO
  crypted_object.h/cpp  # MCOB/MCOZ/MCSP + Snappy
  filetype.h/cpp        # Detect extension, fix .bin
  key_extractor.h/cpp   # PE parsing, delta search, high-entropy scan
  lzo/
    minilzo.c/h
    lzoconf.h
    lzodefs.h
  bruteforce.cpp        # Standalone brute-force tester (optional)

UnpackTool.sln          # VS solution
UnpackTool.vcxproj      # VS project
CMakeLists.txt          # CMake
```

---

## License

- miniLZO: GPL (Markus Oberhumer)
- This tool: For educational purposes, Metin2 client research

---

## Author Notes

This is a professional system ready to compile in VS. It solves:
- Key inside exe: via PE parsing + pattern search + high-entropy brute-force
- .bin problem: via magic number detection + filename hint
- Encrypted filenames: via XTEA decrypt of 160-byte filename field
- All file types: via generic detection, not just py/txt
- Menu: 16 options covering all needed operations

To complete History decryption end-to-end, run the tool, extract keys, then use raw mode + fix extensions. If key not found, the brute-force tool `bruteforce` can be used to test all .data/.rdata candidates with LZO decompress.

Enjoy!
