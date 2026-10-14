# History2.exe Deep Analysis

## PE Info
- 32-bit, image_base 0x400000
- .text VA 0x1000 raw 0x400 size 0x475d800
- .rdata VA 0x475f000 raw 0x475dc00 size 0x535600
- .data VA 0x4c95000 raw 0x4c93200 size 0x3c5800

## XTEA Function
- VA 0x4b21d30 file 0x4721130
- Custom variant, not standard XTEA:
  - Uses `ror ecx, 0x15` (rotate right 21)
  - Deltas: 0x9E3779B9, B8, BB, BA, BD, BC, BF, BE
  - Key access via `[eax+0x00], [eax+0x04], [eax+0x08], [eax+0x0C], [eax+0x10], [eax+0x14], [eax+0x18], [eax+0x1C]` (8 uint32 = 0x20 bytes)
  - Local buffer at `[ebp-0x50]` 0x20 bytes
  - Steps:
    1. memcpy from `[ebx+0x10]` (input data) to local buffer `[ebp-0x50]` size `[ebx+0x14]` (0x20)
    2. memset remaining
    3. For each of 8 dwords in buffer, do xor of 4 other dwords + delta, ror 0x15, store
    4. Write result to `[esi]` where esi = `[ebx+8]` (output key ptr) 0x20 bytes
    5. Then additional loop for larger sizes: `for (i=8; i< size/4; i++) { out[i] = out[i-1] xor out[i-2] xor out[i-3] xor i xor delta ... ror }`

## Wrapper Function
- VA 0x4b223c0 file 0x47217c0
- Bytes: `FF 74 24 08 FF 74 24 08 6A 20 FF B1 30 02 00 00 E8 5B F9 FF FF 83 C4 10 C2 0C 00`
- Disasm:
  ```
  push dword ptr [esp+8]   ; arg2
  push dword ptr [esp+8]   ; arg1 (after first push, this is original arg1)
  push 0x20
  push dword ptr [ecx+0x230] ; key ptr from this+0x230
  call 0x4b21d30            ; custom XTEA
  add esp, 0x10
  ret 0xC
  ```
- Key is at `this+0x230`
- Only reference to `[ecx+0x230]` is this push, no mov found in .text 0x4b20000-0x4b30000 (201 occurrences of 0x230 but mostly ebp-0x230)
- Suggests key init via memcpy from global or via constructor not in that range

## Pack List
- Wide strings at file 0x4767532 VA 0x4b68932
- Error strings at 0x4767920 ("Failed to load pack %s") and 0x4767988
- Loader at 0x77a000-0x77c000 with xrefs at 0x37a47a/0x37a705

## Brute-Force Results
- Scanned .data+.rdata 791317 16-byte high-entropy blocks
- 51 scored >0 with keywords data/pack/.mse etc
- None yielded EPKD after standard XTEA decrypt
- Tested default keys: B99E..., 22B8..., 54D8... -> no EPKD
- Indicates:
  - Key not in plain .data/.rdata, or
  - Needs custom ror variant, or
  - Needs LZO decompress after decrypt, or
  - Key is derived via custom function, not stored plain

## Workplace.d2
- File: History/pack/workplace.d2, 6,126,018 bytes
- Header: `5c ed 0f f0 4d 2f 40 85 4e 9d f3 1c b0 95 c6 27`
- Last 128 high entropy
- Not EPKD, not MCOZ/MCOB
- After standard XTEA decrypt with default keys, still binary, no file list
- After custom key candidates, preview contains "d:/" for key AB77DE3D5F848E2E5C07E5DC17FCA892 at offset 0x4b13a74, score 10, but not full file list

## Next Steps for Full Decryption
1. Implement custom XTEA variant inverse:
   - For each output dword, reverse ror -> rol, then xor to recover input
   - Need to understand full 8-round transformation
2. Find constructor of object containing key at 0x230:
   - Search for `lea ecx, [something]` then call wrapper's class constructor
   - Look for memcpy pattern: push 16, push global, push ecx+0x230, call memcpy
3. Use dynamic analysis: Run exe in debugger, breakpoint at 0x4b21d30, dump key at [ecx+0x230] when pack loading
4. Try LZO decompress after custom XTEA decrypt for workplace.d2

## Tool Support
- UnpackTool already implements:
  - Pattern search for `FF B1 30 02 00 00` (push [ecx+0x230])
  - High-entropy scan with scoring
  - Raw mode decrypt + filetype fix
  - Brute-force tester (bruteforce.cpp) that tries LZO decompress after decrypt

To fully decrypt History, extend `xtea.cpp` with `DecryptBlockCustom()` that mirrors the assembly at 0x4b21d30-0x4b21f60.

