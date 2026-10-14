# Verified History D2 profile

All integers are unsigned 32-bit little-endian. This documentation describes the supplied sample, not Alt2 or a generic Metin2 pack format.

## Archive header (68 bytes)

| Offset | Size | Meaning |
|---|---:|---|
| 0 | 4 | Magic `0xF00FED5C` (`5c ed 0f f0`) |
| 4 | 32 | AES-256 key material |
| 36 | 32 | IV material; AES-CFB uses its first 16 bytes |

The client copies both 32-byte fields and can XOR them with optional external 32-byte masks. The supplied `workplace.d2` verifies without any masks. This tool implements that proven, unmasked profile only.

Because the key and IV live in each archive's own header, every archive is self-describing: the
same code path decrypts `workplace.d2` and any other D2 pack of this profile without per-file
configuration. A file is treated as a History D2 archive **only** when its first four bytes are
`5c ed 0f f0`; the file name and extension are never used to decide. The Alt2 profile in this
repository (`alt2/data/root`, magic `0c ed 0f 00`) is a different format and is rejected.

## Selecting several archives

`--archive` accepts a file or a directory and may be repeated. A directory is searched
recursively up to four levels, with `<directory>/pack` scanned before the directory itself, and
`workplace.d2` is sorted first so it keeps its historical position. Candidate names are any
`*.d2` file plus the extension-less pack names (`root`, `index`, `locale`, `map`, `sound`,
`effect`, `npc`, `item`, `guild`, `season`, `dungeon`, `pack`); each candidate is then confirmed
by the magic, so a misnamed or foreign file is skipped instead of guessed at. Without
`--archive`, the tool searches the working directory and then the executable's directory, up to
seven parents each, stopping at the first level that yields archives.

Each archive keeps its own key/IV, entry table and output folder; nothing is merged across
archives, and a duplicate filename hash in two different archives is not an error (only within
one archive).

## Entry records

First record begins at offset 68. Each record is 20 bytes, immediately followed by its payload.

| Record offset | Meaning |
|---|---|
| 0 | Original size |
| 4 | XXH32 checksum of original bytes; seed `0xF00FED5C` |
| 8 | Absolute payload offset |
| 12 | Stored payload size |
| 16 | Normalized filename CRC32 |

The next record is at `payload_offset + stored_size`. There is no separate file count and no filename text. Parsing ends exactly at archive EOF. This implementation requires contiguous records, forward progress, unique filename hashes and all payload ranges to be in bounds.

## Decode sequence

1. Initialize AES-256 with the header key.
2. Initialize a 16-byte feedback register with header bytes 36–51.
3. AES-encrypt the feedback register, XOR with up to 16 ciphertext bytes, replace feedback with the ciphertext block; repeat (CFB128 decryption, no padding).
4. If original size differs from stored size, decode as a raw LZ4 block, with strict input/output bounds.
5. Require exact original size and matching XXH32.
6. Only then export bytes.

Each entry starts with a fresh cipher state. No additional file-type conversion, newline normalization, text decoding or extension inference occurs.

## Filename lookup

Normalize ASCII letters to lowercase; change `\` to `/`. Compute standard reflected CRC32 (polynomial `0xEDB88320`, initial and final XOR `0xFFFFFFFF`). Paths are relative to the virtual filesystem, not automatically prefixed with `root/`.

Candidate collisions are retained as ambiguous. The bundled dictionary and reference scanning are recovery aids, not a reversible hash function.

## Static analysis evidence

For the supplied 32-bit `History2.exe` at preferred image base `0x00400000`:

- VA `0x008E0610`: archive open/header parsing, magic comparison, optional mask XOR and entry iteration.
- VA `0x008E0360`: payload reading/decryption, optional decompression and checksum verification.
- VA `0x008DD9D0`: lowercase/separator normalization and Crypto++ CRC32 filename hashing.
- VA `0x008DE3B0` and RTTI associated with `0x04B95A00` / `0x04B95B34`: Rijndael encryption primitive and CFB decryption mode.
- VA `0x049ACA80`: XXH32 checksum routine.
- VA `0x049ADEC0`: raw LZ4 decompression routine.

These addresses document analysis, not hardcoded runtime offsets. The tool does not load or call client code.

Sample: 813 verified entries in a 6,126,018-byte archive. Independent aggregate SHA-256 over records sorted by filename hash, each encoded as `(uint32 hash LE, uint64 original length LE, original payload bytes)`:

`500a48d43bd2419bc33dc194e6b3dade42afbaf8996735dfc2c53b859a782daa`
