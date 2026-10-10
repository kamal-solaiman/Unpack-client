#!/usr/bin/env python3
"""Read-only extractor for the supplied History .d2 pack. Never runs the client.

The archive embeds its key and IV. The matching client defines their use; see
FORMAT.md. Filenames cannot be recovered from the archive's 32-bit name hashes.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import tempfile

HERE = Path(__file__).resolve().parent
MAGIC = 0xF00FED5C
HEADER = struct.Struct("<5I")
FIRST_ENTRY = 0x44
CLIENT_SHA256 = "a5b8787ff8478028c19dfce124f5f9dec8e07b333abf875e95f54b67d9c8fd3a"
DEFAULT_FILE_LIMIT = 128 * 1024 * 1024
DEFAULT_TOTAL_LIMIT = 1024 * 1024 * 1024


class UnpackError(Exception):
    """Bad, unsupported or unsafe input."""


def dependencies():
    try:
        from Crypto.Cipher import AES
        import lz4.block
        import xxhash
    except ImportError as exc:
        raise UnpackError("Install dependencies: python -m pip install -r History/requirements.txt") from exc
    return AES, lz4.block, xxhash


@dataclass(frozen=True)
class Entry:
    index: int
    header_offset: int
    original_size: int
    checksum: int
    data_offset: int
    stored_size: int
    name_hash: int


def read_index(path: Path, max_file_size: int = DEFAULT_FILE_LIMIT,
               max_total_size: int = DEFAULT_TOTAL_LIMIT) -> tuple[bytes, bytes, list[Entry]]:
    """Read just the 68-byte preamble and 20-byte headers; bound all allocations."""
    size = path.stat().st_size
    if size < FIRST_ENTRY:
        raise UnpackError("Truncated archive header")
    with path.open("rb") as src:
        preamble = src.read(FIRST_ENTRY)
        if struct.unpack_from("<I", preamble)[0] != MAGIC:
            raise UnpackError("Not a History .d2 archive (bad magic)")
        key, iv = preamble[4:36], preamble[36:68]
        entries: list[Entry] = []
        offset = FIRST_ENTRY
        total = 0
        while offset < size:
            if size - offset < HEADER.size:
                raise UnpackError(f"Truncated entry header at 0x{offset:x}")
            src.seek(offset)
            original_size, checksum, data_offset, stored_size, name_hash = HEADER.unpack(src.read(HEADER.size))
            index = len(entries)
            if data_offset != offset + HEADER.size:
                raise UnpackError(f"Invalid payload offset in entry {index}")
            if not stored_size or not original_size or data_offset + stored_size > size:
                raise UnpackError(f"Invalid size / truncated payload in entry {index}")
            total += original_size
            if (original_size > max_file_size or stored_size > max_file_size
                    or total > max_total_size):
                raise UnpackError(f"Size safety limit exceeded in entry {index}")
            entries.append(Entry(index, offset, original_size, checksum, data_offset, stored_size, name_hash))
            if len(entries) > 1_000_000:
                raise UnpackError("Too many entries")
            offset = data_offset + stored_size
    if not entries:
        raise UnpackError("Archive has no entries")
    return key, iv, entries


def decode(src, entry: Entry, key: bytes, iv: bytes) -> bytes:
    AES, lz4_block, xxhash = dependencies()
    src.seek(entry.data_offset)
    ciphertext = src.read(entry.stored_size)
    if len(ciphertext) != entry.stored_size:
        raise UnpackError(f"Truncated payload in entry {entry.index}")
    # Crypto++ CFB_DecryptionTemplate uses full AES blocks (128-bit feedback).
    plaintext = AES.new(key, AES.MODE_CFB, iv=iv[:16], segment_size=128).decrypt(ciphertext)
    if entry.stored_size == entry.original_size:
        decoded = plaintext
    else:
        try:
            decoded = lz4_block.decompress(plaintext, uncompressed_size=entry.original_size)
        except (lz4_block.LZ4BlockError, ValueError, OverflowError) as exc:
            raise UnpackError(f"LZ4 decode failed in entry {entry.index}: {exc}") from exc
    if len(decoded) != entry.original_size:
        raise UnpackError(f"Size mismatch in entry {entry.index}")
    if xxhash.xxh32(decoded, seed=MAGIC).intdigest() != entry.checksum:
        raise UnpackError(f"XXH32 mismatch in entry {entry.index}: wrong key or corrupt archive")
    return decoded


def client_fingerprint(path: Path) -> str:
    """Identify the examined PE build; this does not claim its key is in the PE."""
    digest = hashlib.sha256()
    with path.open("rb") as src:
        if src.read(2) != b"MZ":
            raise UnpackError("Client is not a PE executable")
        src.seek(0)
        for block in iter(lambda: src.read(1024 * 1024), b""):
            digest.update(block)
    result = digest.hexdigest()
    if result != CLIENT_SHA256:
        raise UnpackError("Unsupported History2.exe build; its archive loading behavior has not been verified "
                          f"(SHA-256: {result})")
    return result


def extension(data: bytes) -> str:
    # Extension is a convenience classification, NEVER a recovered filename.
    if data.startswith(b"\x03\xf3\r\n"):
        return ".pyc"  # CPython 2.7 bytecode; never execute it
    if data.startswith((b"#", b"import ", b"from ", b"\r\n", b"\n")):
        return ".py"  # best-effort; use the manifest for authoritative metadata
    return ".bin"


def run(path: Path, output: Path | None, max_file_size: int, max_total_size: int) -> tuple[int, int]:
    key, iv, entries = read_index(path, max_file_size, max_total_size)
    if output is not None:
        if output.exists() or output.is_symlink():
            raise UnpackError(f"Output already exists: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.parent.is_dir():
            raise UnpackError(f"Output parent is not a directory: {output.parent}")
    temp: Path | None = None
    try:
        if output is not None:
            temp = Path(tempfile.mkdtemp(prefix=".history-unpack-", dir=output.parent))
        manifest = []
        with path.open("rb") as src:
            for entry in entries:
                decoded = decode(src, entry, key, iv)
                if temp is not None:
                    name = f"{entry.index:04d}_{entry.name_hash:08x}{extension(decoded)}"
                    (temp / name).write_bytes(decoded)
                    manifest.append({**asdict(entry), "checksum": f"{entry.checksum:08x}",
                                     "name_hash": f"{entry.name_hash:08x}",
                                     "output": name, "sha256": hashlib.sha256(decoded).hexdigest()})
        if temp is not None:
            (temp / "manifest.json").write_text(json.dumps({
                "archive": str(path.resolve()), "format": "History d2 / AES-256-CFB / raw LZ4 / XXH32",
                "note": "Output names are index and hash placeholders, NOT the original filenames.",
                "entries": manifest,
            }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            if output.exists() or output.is_symlink():
                raise UnpackError(f"Output appeared during extraction: {output}")
            temp.rename(output)
            temp = None
    finally:
        if temp is not None:
            shutil.rmtree(temp)
    return len(entries), sum(e.original_size for e in entries)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("key", "list", "verify", "extract"))
    parser.add_argument("archive", nargs="?", type=Path, default=HERE / "pack/workplace.d2")
    parser.add_argument("--client", type=Path, default=HERE / "History2.exe",
                        help="PE build checked by 'key'; the archive itself holds its key")
    parser.add_argument("-o", "--output", type=Path, default=HERE / "unpacked/workplace")
    parser.add_argument("--max-file-size", type=int, default=DEFAULT_FILE_LIMIT)
    parser.add_argument("--max-total-size", type=int, default=DEFAULT_TOTAL_LIMIT)
    args = parser.parse_args(argv)
    try:
        if min(args.max_file_size, args.max_total_size) <= 0:
            raise UnpackError("Size limits must be positive")
        key, iv, entries = read_index(args.archive, args.max_file_size, args.max_total_size)
        if args.command == "key":
            print("History2.exe SHA-256:", client_fingerprint(args.client))
            print("The client reads a 64-byte key/IV preamble from the .d2 header; "
                  "this archive uses no additional client-side XOR masks.")
            print("Archive AES-256 key (offset 0x04):", key.hex())
            print("Archive IV material (offset 0x24):", iv.hex())
            print("AES-CFB IV used (first 16 bytes):", iv[:16].hex())
            print("Checking first entry:", end=" ")
            with args.archive.open("rb") as src:
                decode(src, entries[0], key, iv)
            print("XXH32 verified")
        elif args.command == "list":
            print("index  name_hash  original  stored  data_offset")
            for e in entries:
                print(f"{e.index:5d}  {e.name_hash:08x}  {e.original_size:8d}  "
                      f"{e.stored_size:6d}  0x{e.data_offset:08x}")
            print(f"{len(entries)} entries; filenames are not present in archive")
        else:
            out = args.output if args.command == "extract" else None
            count, total = run(args.archive, out, args.max_file_size, args.max_total_size)
            print(f"Verified {count}/{count} entries ({total:,} decoded bytes)")
            if out is not None:
                print(f"Extracted to {out}")
        return 0
    except (UnpackError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
