# History `.d2` format — supplied build

Reverse-engineered **statically** from the supplied 32-bit PE (`History2.exe`), then checked by decoding and verifying all 813 entries of `pack/workplace.d2`. Neither executable nor extracted bytecode was run. This format differs from ALT2's archive format.

## Input fingerprints (SHA-256)

```text
History2.exe          a5b8787ff8478028c19dfce124f5f9dec8e07b333abf875e95f54b67d9c8fd3a
pack/workplace.d2      a0ddcf7eeec86ad648062c73ee2d5985b019fc6e32ae4ac4636648426553e049
```

## Preamble and records

All integers are little-endian `uint32`. The archive begins with 68 bytes:

| Offset | Length | Meaning |
|---:|---:|---|
| `0x00` | 4 | Magic `0xF00FED5C` (bytes `5c ed 0f f0`) |
| `0x04` | 32 | Per-archive AES-256 key |
| `0x24` | 32 | IV material (first 16 bytes used for AES-CFB) |
| `0x44` | 20 | First entry header |

Each entry header is 20 bytes, immediately followed by an encrypted payload. The next header is at `data_offset + stored_size`. There is no count or plaintext filename table; walk to EOF.

| Relative offset | Field | Meaning |
|---:|---|---|
| `+0x00` | `original_size` | Decoded length |
| `+0x04` | `checksum` | XXH32 of decoded bytes, seed `0xF00FED5C` |
| `+0x08` | `data_offset` | Absolute payload position: header offset + 20 |
| `+0x0C` | `stored_size` | Encrypted payload length (no block-size padding) |
| `+0x10` | `name_hash` | Hash of normalized virtual filename, **not** a filename |

First entry at `0x44`:

```text
original_size  29428
checksum       0xC0B1B963
data_offset    0x58
stored_size    8529
name_hash      0x75A4D836
next header    0x21A9
```

## Decoding

1. Reset AES-256-CFB for **each** entry, with the header's 32-byte key and the **first 16 bytes** of IV material. Use **128-bit CFB feedback** (e.g. PyCryptodome `segment_size=128`, not its default 8-bit CFB).
2. If `stored_size == original_size`, use decrypted bytes directly. Otherwise decompress as a **raw LZ4 block**, supplying `original_size`; there is no LZ4 frame or prepended size.
3. Check decoded length and seeded XXH32 before accepting the file. Never execute decoded code.

All 813 records in this sample take the LZ4 branch, consume the archive exactly through EOF, and pass both checks. The first one decrypts to a raw LZ4 block whose output begins `##################################################\r\n## NAME: Camy`.

## What the EXE provides (and what it does not)

The examined PE is x86 with preferred image base `0x00400000`. Relevant preferred virtual addresses (not raw file offsets):

| VA | Role |
|---|---|
| `0x008E0610` | Open pack, read 0x44-byte preamble, compare magic; copy key and IV material; optionally XOR each with a pack-specific 32-byte mask |
| `0x008E0794` | Read 20-byte record, advance through payloads |
| `0x008E0360` | Fetch an entry, decrypt and validate |
| `0x008E043D` | Construct the per-entry decryption pipeline |
| `0x008E046A` | XXH32 verification with seed `0xF00FED5C` |

The pack-specific XOR masks are optional arguments to the loader; this supplied archive verifies with **no masks**. The actual key and IV for `workplace.d2` are in its preamble, not hardcoded in this PE. `unpack.py key` pins the analyzed client by SHA-256 and reports these archive header values, verifying the first entry. It does not extract a nonexistent hardcoded EXE key or claim support for modified executables or every other `.d2` pack.

The name hash is not reversible into a unique pathname; output is deliberately indexed by hash. A `.pyc` suffix means Python 2.7 bytecode was preserved, not decompiled. Default per-file and total decoded size limits are 128 MiB and 1 GiB respectively.
