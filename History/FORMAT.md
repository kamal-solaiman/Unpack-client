# History pack format — supplied build

These observations were obtained by statically inspecting the supplied 32-bit PE (`History2.exe`) and
verified by decoding every entry of `pack/workplace.d2`. No Windows executable, pack, or extracted
Python file was run, and no input file was modified.

Unlike the ALT2 sample, **this container carries its own key material in the archive header**. The
client is still required: `unpack.py` derives the magic, the header geometry, the cipher, the key
length and the IV position from the client's machine code instead of hardcoding them, and refuses
builds it cannot prove.

## Input fingerprints (SHA-256)

```text
History2.exe          89,526,784 bytes, PE32 i386, ImageBase 0x00400000
a5b8787ff8478028c19dfce124f5f9dec8e07b333abf875e95f54b67d9c8fd3a

pack/workplace.d2      6,126,018 bytes
a0ddcf7eeec86ad648062c73ee2d5985b019fc6e32ae4ac4636648426553e049
```

## Container layout

All integer fields are unsigned 32-bit **little-endian**.

| Offset | Size | Field |
|---:|---:|---|
| `0x00` | 4 | Magic `0xF00FED5C` (`5c ed 0f f0`) — also the XXH32 seed |
| `0x04` | 32 | AES-256 key |
| `0x24` | 16 | CFB initialization vector |
| `0x34` | 16 | Reserved: copied into the archive object, never used by the cipher |
| `0x44` | … | Chain of entry headers and payloads |

Each entry header is 20 bytes:

| Relative offset | Field | Meaning |
|---:|---|---|
| `+0x00` | `original_size` | Decoded file length |
| `+0x04` | `checksum` | XXH32 of the decoded file, seed `0xF00FED5C` |
| `+0x08` | `data_offset` | Absolute payload offset |
| `+0x0C` | `stored_size` | Encrypted payload length (LZ4-compressed unless it equals `original_size`) |
| `+0x10` | `name_hash` | CRC32 of the normalized virtual filename |

The client walks the chain like this (`0x8E078B`–`0x8E07FC`):

```text
position = 0x44
while position < file_size:
    seek(position); read 20 bytes
    position = data_offset + stored_size
```

In this archive `data_offset == header_offset + 20` for every entry and the chain ends exactly at EOF:
**813 entries**, **16,929,395 decoded bytes**, 813 distinct name hashes, no trailing bytes. All 813
payloads are LZ4-compressed; the client also supports the stored case (`stored_size == original_size`),
which the tool handles by skipping decompression.

## Decode pipeline for one entry

1. Seek to `data_offset`, read `stored_size` bytes.
2. Decrypt with **AES-256 in CFB mode with full-block feedback** (CFB128 — the Crypto++ `CFB_Mode`
   default). The client builds a fresh cipher object per read (`0x8E043D`, `0x8E0502`), so the **IV
   restarts for every entry**; the same key and IV are reused across the whole archive. CFB is a stream
   mode, so `stored_size` needs no padding or alignment.
3. If `stored_size == original_size`, the plaintext is the file. Otherwise decode a **raw LZ4 block**
   (not an LZ4 frame) with the original length taken from the header.
4. Verify `len(payload) == original_size` and `XXH32(payload, seed=0xF00FED5C) == checksum`. A wrong
   key or damaged archive must never be published as a successful extraction.

Recovered key material for the supplied pack (`unpack.py key` prints it):

```text
key (32) 4d2f40854e9df31cb095c62702992a0f0e35f6416a5456b94e3d9fefad1de7b8
iv  (16) 4981ad462f28d3ed30b4b9f32a1b4ae8
res (16) 2dd6c2e9a98fab4469ab75e7b40a5f32
```

## Filename hashing

`name_hash` is the **CRC32** (polynomial `0xEDB88320`, table at `0x4F14840`) of the name after the
client's normalization at `0x8DD9D0`: ASCII `tolower`, then every `\` becomes `/`. The whole 32-bit
digest is the key; the client then runs FNV-1a (`0x811C9DC5` / `0x01000193`) over those four bytes only
to pick a hash-map bucket (`0x762C60`), which is why both hash constants appear in the code.

Names are not stored in the archive. `unpack.py` recovers them by CRC32-matching candidate strings
harvested from two sources:

* the client's own ASCII and UTF-16 string pool, which contains real script paths such as
  `uiscript\beltinventorywindow.py` (embedded `co_filename` values), and
* the decoded payloads: path literals, `import` statements, and the directories they reveal
  (for example `uiscript/`, which then names bare module tokens).

A hash is named only when **exactly one** candidate matches; ambiguous hashes stay in `unknown/`.
Result for the supplied pack: **812 of 813 named, 0 ambiguous**. The single unnamed entry is index 468
(`ff6e5d2d`, 67,642 bytes), a Markdown guide whose filename appears neither in the pack nor in the
client — supply it with `--names` if you know it.

## Optional per-pack key masks

`Open(this, path, key_mask, iv_mask)` at `0x8E0610` copies `header[4..68]` into the archive object and
then XORs the 32 key bytes and the 32 IV/reserved bytes with the two masks (`0x8E070E`–`0x8E0788`,
eight `xor [esi+disp], eax` instructions). Its caller (`0x8DDE64`–`0x8DDE82`) takes the masks from a
`std::map<std::string, …>` keyed by the pack filename: `node+0x28` for the key and `node+0x48` for the
IV, and passes **NULL when the name is not in the map**, which skips the XOR entirely.

The client knows 43 pack names (`data.d2`, `patch.d2`, `etc.d2`, `icon.d2`, `item.d2`, `map.d2`,
`monster.d2`, `npc.d2`, `pc_*.d2`, `seasons.d2`, `sound.d2`, `terrain.d2`, `zone.d2`, `locale.d2`, …,
listed at `0x422E90`) and loads them from `<client directory>\pack` (`0x77AF90`). The string
`workplace` does **not** occur anywhere in `History2.exe` (ASCII or UTF-16), so no mask can apply to
this pack — confirmed empirically: all 813 entries verify with the header key used verbatim.
`--key-mask` / `--iv-mask` (hex) exist for packs whose names do appear in that table.

## How the tool derives the geometry from the client

`analyze_client()` never assumes a constant; it walks an evidence chain and fails loudly if any step is
ambiguous:

1. **Find XXH32**: locate `imul …, 0x7A143589` (`-PRIME2`) with `0x9E3779B1` (`PRIME1`) within ±64 bytes.
2. **Derive the magic**: collect `cmp dword ptr [reg], imm32` and `push imm32` immediates in executable
   sections. The magic is the one immediate that is compared exactly once and pushed at least twice,
   where every push is followed within 24 bytes by `call rel32` into the XXH32 routine → `0xF00FED5C`.
3. **Find the pack-open routine**: the single `cmp dword ptr [edi], 0xF00FED5C` (`0x8E06C2`).
4. **Derive the blob copy**: parse the alternating `movups` load/store chain that follows it
   (`0F 10` / `0F 11` with plain `[base+disp]` operands): loads `0x64, 0x74, 0x84, 0x94`, stores
   `0x20, 0x30, 0x40, 0x50` → a contiguous 64-byte blob copied from header offset `0x64 - 0x60 = 4`.
5. **Derive the header size**: match `push imm8; lea reg, [base+disp8]; push reg` (`0x8E06A2`:
   `push 0x44; lea edi,[esi+0x60]; push edi`) and keep only the read whose size is consistent with the
   copied blob (`0x44 == 4 + 64`) → header size 68, buffer at object `+0x60`.
6. **Derive the key split**: match the cipher-construction argument chain
   `lea eax,[esi+A]; … ; push eax; push keylen; lea eax,[esi+B]; push eax` — two sites, `0x8E0426` and
   `0x8E04EE`, both `A = 0x40`, `keylen = 0x20`, `B = 0x20` → key length 32 (AES-256), key at header
   offset 4, IV at header offset `4 + (0x40 - 0x20) = 36`, one AES block (16 bytes), 16 reserved bytes.
7. **Confirm the primitives**: the AES S-box must exist and be referenced from executable code
   (`0x4F172E0`, 61 references); the CRC32 table, the LZ4 token loop and the `\`→`/` normalization
   bytes are reported as landmarks; `CFB`, `AES` and `FeedbackSize` mode descriptors sit beside the
   cipher vtables.
8. **Prove the result**: `unpack.py key` decrypts the first entries and checks their XXH32 values.

If any step yields zero or several answers, the tool stops with an error rather than guessing offsets.

## Static-analysis landmarks

Preferred virtual addresses (ImageBase `0x00400000`), not file offsets or ASLR runtime addresses.

| Address | Observed role |
|---|---|
| `0x8E0610` | Pack open: `CreateFileW`, read the `0x44`-byte header, magic check, blob copy, optional masks, index walk |
| `0x8E06A2` | `push 0x44; lea edi,[esi+0x60]; push edi` → `ReadFile` of the header |
| `0x8E06C2` | `cmp dword ptr [edi], 0xF00FED5C` — the magic check (error 9 otherwise) |
| `0x8E06E1`–`0x8E0706` | `movups` chain copying `header[4..68]` into object `+0x20..+0x60` |
| `0x8E0710`–`0x8E0788` | Optional XOR of the key blob and the IV blob with the two masks |
| `0x8E0794`–`0x8E07FC` | Index walk: `SetFilePointerEx`, `ReadFile(0x14)`, insert into the hash map |
| `0x8DFEF0` | Entry read: seek, read, decrypt, optional LZ4, XXH32 verify |
| `0x8E0426`, `0x8E04EE` | Cipher argument chain: IV pointer, key length `0x20`, key pointer |
| `0x8DE3B0` | Cipher constructor: builds the CFB mode object, registers the `IV` parameter |
| `0x49E15A0` | `SetKey(key, length, parameters)` — validates the key length first |
| `0x49FC0C0` | Stream-transformation dispatch that decrypts `(src, dst, size)` in place |
| `0x4F172E0` | AES S-box (61 code references; inverse S-box at `0x4F173E0`) |
| `0x4B959F4`, `0x4B959F8`, `0x4B95984` | `"CFB"`, `"AES"`, `"FeedbackSize"` mode descriptors |
| `0x49ACA80` | XXH32(data, len, seed); round-loop constants at `0x49ACAC2` |
| `0x8E046A`, `0x8E055C` | `push 0xF00FED5C` — the XXH32 seed at both verification sites |
| `0x49ADEC0` | Raw LZ4 block decoder (token-loop signature at `0x49ADED5`) |
| `0x8DD9D0` | Name → hash: ASCII tolower, `\`→`/`, CRC32, first 4 bytes |
| `0x8DDA89` | `cmp byte ptr [ecx+eax],0x5C` / `mov byte ptr [ecx+eax],0x2F` |
| `0x4F14840` | CRC32 table (`00000000 77073096 EE0E612C 990951BA …`) |
| `0x762C60`, `0x8DE1C0` | Index lookup by name hash (FNV-1a bucket) / index insert |
| `0x8DDE64`–`0x8DDE82` | Per-pack mask lookup; NULL masks when the name is unknown |
| `0x422E90` | Builds the ordered list of the 43 known `.d2` pack names |
| `0x77AF90` | Builds the `<client directory>\pack` root path |
| `0x4B5F160`, `0x4B5F254`, `0x4B5F278` | IAT: `SetFilePointerEx`, `ReadFile`, `CreateFileW` |

Archive object layout used by those routines: `+0x20` key (32), `+0x40` IV (16), `+0x50` reserved (16),
`+0x60` raw header copy (68), `+0xA4` file handle, `+0xA8` pack path (wide, up to `0x20A` bytes).
Index nodes are 0x28 bytes: `+0x10`/`+0x14` the 64-bit payload offset, `+0x18` `stored_size`,
`+0x1C` `original_size`, `+0x20` `checksum`.

## Differences from the ALT2 container in this repository

| | ALT2 (`alt2/data/root`) | History (`pack/workplace.d2`) |
|---|---|---|
| Magic | `0x000FED0C` | `0xF00FED5C` |
| Key location | 16-byte XTEA key inside the EXE | 32-byte AES key inside the pack header |
| Cipher | XTEA, 4 cycles, ECB layout, 8-byte blocks, zero padding | AES-256-CFB128, stream, IV restarted per entry, no padding |
| Entry header | 24 bytes, separate `compressed_size` | 20 bytes, `stored_size == original_size` means "not compressed" |
| Index start | offset 4 | offset `0x44` |
| Compression | raw LZ4 block | raw LZ4 block |
| Checksum | XXH32 seeded with the magic | XXH32 seeded with the magic |
| Name hash | CRC32 of the normalized name | CRC32 of the normalized name |

## Verified results for the supplied sample

```text
entries                813
verified (size+XXH32)  813   (100%)
decoded bytes          16,929,395
named                  812   (99.9%)
ambiguous names        0
unknown                1     (index 468, ff6e5d2d, Markdown guide)
```

Contents: the client's Python 2.7 UI layer — 569 `.py` sources, 242 `.pyc` byte-code files, one
`claude.md` overview, and the unnamed Markdown guide; 340 files live under `uiscript/`. Reproduce with
`HISTORY_FULL_TEST=1 python -m unittest discover -s History/tests -t History/tests`.
