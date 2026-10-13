# ALT2 archive format — supplied build

These observations were obtained by statically inspecting the supplied x64 PE and verified by decoding every entry of `data/root`. No Windows executable or extracted Python code was run. This is not the traditional paired EIX/EPK format.

## Input fingerprints (SHA-256)

```text
metin2client.exe
7ed5f6f2864b63025508e1870c1d28fe286b919e26b4c23f665896c02e717fbd

data/root
895821bc4da72205793c5bb2cc12fc0ebabc2da9cb4cc85cdfb653d3973a989b
```

## Container layout

All integer fields are unsigned 32-bit **little-endian**. The file starts with the four-byte magic `0x000FED0C` (`0c ed 0f 00`). Headers and payloads are interleaved; there is no separate filename table or entry-count field.

Starting at offset 4, each 24-byte header has this structure:

| Relative offset | Field | Meaning |
|---:|---|---|
| `+0x00` | `original_size` | Decoded file length |
| `+0x04` | `stored_size` | Encrypted payload length, padded to 8 bytes |
| `+0x08` | `checksum` | XXH32 of the final decoded file, seed `0x000FED0C` |
| `+0x0C` | `data_offset` | Absolute payload offset in the archive |
| `+0x10` | `compressed_size` | Meaningful payload length before encryption padding |
| `+0x14` | `name_hash` | CRC32 of the normalized virtual filename |

The observed layout requires:

```text
data_offset = header_offset + 24
stored_size = (compressed_size + 7) & ~7
next_header = data_offset + stored_size
```

Walk records until EOF. The supplied archive has 894 records, all with distinct filename hashes, and no trailing bytes. Of these, 173 have `compressed_size == original_size` (stored without LZ4 compression, but still encrypted).

## Encryption and decompression

1. Read `stored_size` encrypted bytes.
2. Decrypt independent 8-byte blocks using **XTEA in ECB layout, four cycles** (eight half-rounds), with two little-endian 32-bit words per block. This is **not** standard 32-cycle XTEA, TEA, or XXTEA.
3. Discard encryption padding beyond `compressed_size`. Do not apply PKCS#7 unpadding.
4. If `compressed_size == original_size`, the resulting bytes are the file itself.
5. Otherwise decode a **raw LZ4 block**, not an LZ4 frame; the original length comes from the entry header. The client uses a fast decompressor returning consumed input size; the tool uses the bounded `lz4.block.decompress` interface and checks output length.
6. Verify the final size and seeded XXH32 against the header. A wrong key or corrupt file must not be published as successful extraction.

XTEA uses delta `0x9E3779B9`. Decryption starts at sum `4 * delta mod 2^32 = 0x78DDE6E4`.

## Statically recovered key

```text
Bytes: 54 d8 20 39 aa 8d 27 22 dc 23 e8 1c 69 6b 74 30
Words: 0x3920D854 0x22278DAA 0x1CE823DC 0x30746B69

Preferred image base: 0x140000000
Key RVA:              0x00937F60
Key file offset:      0x00936B60
Key preferred VA:     0x140937F60
```

The tool does **not** blindly read this file offset. It parses PE sections, searches executable sections for the unrolled XTEA-4 routine, resolves four RIP-relative loads, and checks that the loads reference `key+0`, `key+12`, `key+4`, and `key+8`. It requires exactly one supported routine and maps its key RVA back to file-backed data. Changing compilation, obfuscation, or runtime key initialization can require a new signature/analysis; this is deliberately not advertised as universal key recovery.

## Static-analysis landmarks

Addresses below are preferred virtual addresses for the supplied executable, not file offsets or ASLR runtime addresses.

| Address | Observed role |
|---|---|
| `0x1403B6790` | Filename normalization and CRC32 |
| `0x1403B6920` | XTEA-4 decryption function |
| `0x1403B6960` | Unrolled block loop used by the key signature |
| `0x1403B6AD0` | Entry lookup, decryption, optional decompression, and checksum verification |
| `0x1403B71E3` | Archive magic comparison |
| `0x1403B723A` | Read 24-byte entry header |
| `0x14068DD60` | Raw LZ4 decompression routine |
| `0x140692E20` | Seeded XXH32 routine |

## Filename hashes

The client replaces `\\` with `/`, lowercases ASCII letters, and computes standard CRC32. For example:

```text
CRC32("assassin_m.msm") = 0x6E2DEEFD
CRC32("assassin_w.msm") = 0x447D61DE
```

The first record illustrates all fields:

```text
header_offset:   4
original_size:   79675
stored_size:     15456
checksum:       0xB34005B5
data_offset:    28
compressed_size:15452
name_hash:      0x6E2DEEFD
```

Its first encrypted block is `17 8b 82 d7 29 96 02 59`. Decryption gives `b7 53 63 72 69 70 74 54`, the start of an LZ4 token followed by `ScriptT`. LZ4 decoding produces a `RaceDataScript` file, whose XXH32 matches the header.

Names are inferred, not decrypted. CRC32 cannot reconstruct an arbitrary original filename and is not collision-resistant. Matching candidates come from three bounded sources: references in the client and decoded payloads (paths, Python imports, static string concatenations, directory + basename pairs), a deterministic generation phase that combines observed directories with bare basenames, enumerates one- and two-character stems against common extensions, and pairs identifier tokens with extensions, and user-supplied `--names` lists. A candidate is accepted only when its CRC32 matches an entry hash; collisions remain possible in principle. Ambiguous candidates remain unnamed. Unnamed payloads are labelled with a best-effort content type (magic bytes for PNG/JPG/DDS/TGA/RIFF/Ogg/Granny/TTF/BMP, text heuristics for Python/XML/MSM/MSA/TXT) that picks their `unknown/` extension, and the manifest records that type. The manifest preserves every index, original hash, size, output path, candidate set, content type where applicable, and the SHA-256 of the decoded content.

## Verified result

- 894 / 894 entry sizes and XXH32 checks matched.
- 52,614,417 bytes decoded from 36,796,636 archive bytes.
- 337 names inferred automatically (308 from references, 29 from the generation phase); 557 payloads retained under indexed, content-typed names (216 txt, 201 png, 108 tga, 8 py, 5 xml, 5 dds, 4 avi, 10 bin).
- Original archive and executable remained unchanged.

The default extraction directory is ignored by Git to avoid checking in regenerated assets. Reproduce with the commands in [README.md](README.md).
