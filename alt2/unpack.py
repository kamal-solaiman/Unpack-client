#!/usr/bin/env python3
"""Read-only unpacker for the supplied ALT2 client (XTEA-4 / LZ4 / XXH32).

The Windows client and extracted scripts are NEVER executed. See README.md
for the format, name recovery limitations, and command-line examples.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import tempfile
import zlib

MAGIC = 0x000FED0C
MASK = 0xFFFFFFFF
DELTA = 0x9E3779B9
HEADER = struct.Struct("<6I")
HERE = Path(__file__).resolve().parent
DEFAULT_FILE_LIMIT = 128 * 1024 * 1024
DEFAULT_TOTAL_LIMIT = 1024 * 1024 * 1024


class UnpackError(Exception):
    """Unsupported, corrupt, or unsafe input."""


def dependencies():
    try:
        import lz4.block
        import xxhash
    except ImportError as exc:
        raise UnpackError("Install dependencies: python -m pip install -r alt2/requirements.txt") from exc
    return lz4.block, xxhash


@dataclass(frozen=True)
class Entry:
    index: int
    header_offset: int
    original_size: int
    stored_size: int
    checksum: int
    data_offset: int
    compressed_size: int
    name_hash: int


def read_index(path: Path, max_file_size: int = DEFAULT_FILE_LIMIT,
               max_total_size: int = DEFAULT_TOTAL_LIMIT) -> list[Entry]:
    """Walk the interleaved headers and payloads; reject gaps and truncation."""
    size = path.stat().st_size
    entries = []
    total = 0
    with path.open("rb") as stream:
        if stream.read(4) != struct.pack("<I", MAGIC):
            raise UnpackError("Not an ALT2 archive: expected magic 0x000fed0c")
        position = 4
        while position < size:
            stream.seek(position)
            data = stream.read(HEADER.size)
            if len(data) != HEADER.size:
                raise UnpackError(f"Truncated header at 0x{position:x}")
            entry = Entry(len(entries), position, *HEADER.unpack(data))
            if entry.data_offset != position + HEADER.size:
                raise UnpackError(f"Invalid payload offset at entry {entry.index}")
            if entry.stored_size != ((entry.compressed_size + 7) & ~7):
                raise UnpackError(f"Invalid encrypted block size at entry {entry.index}")
            if entry.data_offset + entry.stored_size > size:
                raise UnpackError(f"Truncated payload at entry {entry.index}")
            total += entry.original_size
            if max(entry.original_size, entry.stored_size) > max_file_size or total > max_total_size:
                raise UnpackError(f"Size safety limit exceeded at entry {entry.index}")
            if not entry.compressed_size and entry.original_size:
                raise UnpackError(f"Empty payload for nonempty entry {entry.index}")
            entries.append(entry)
            if len(entries) > 1_000_000:
                raise UnpackError("Too many entries")
            position = entry.data_offset + entry.stored_size
    return entries


class PEImage:
    """Minimal bounds-checked PE32+ mapping, without loading executable code."""

    def __init__(self, data: bytes):
        self.data = data
        try:
            if data[:2] != b"MZ":
                raise ValueError("missing MZ signature")
            pe = struct.unpack_from("<I", data, 0x3C)[0]
            if data[pe:pe + 4] != b"PE\0\0":
                raise ValueError("missing PE signature")
            machine, count = struct.unpack_from("<HH", data, pe + 4)
            optional_size = struct.unpack_from("<H", data, pe + 20)[0]
            if machine != 0x8664 or struct.unpack_from("<H", data, pe + 24)[0] != 0x20B:
                raise ValueError("expected an x64 PE32+ client")
            if not 1 <= count <= 96 or optional_size < 32:
                raise ValueError("invalid PE header")
            self.image_base = struct.unpack_from("<Q", data, pe + 48)[0]
            self.sections = []
            for i in range(count):
                off = pe + 24 + optional_size + i * 40
                name, _, rva, length, raw = struct.unpack_from("<8s4I", data, off)
                flags = struct.unpack_from("<I", data, off + 36)[0]
                if raw + length > len(data):
                    raise ValueError("truncated PE section")
                self.sections.append((name.rstrip(b"\0"), rva, raw, length, flags))
        except (struct.error, ValueError) as exc:
            raise UnpackError(f"Invalid client executable: {exc}") from exc

    def rva_to_offset(self, rva: int, length: int) -> int:
        for _, start, raw, size, _ in self.sections:
            if start <= rva and rva + length <= start + size:
                return raw + rva - start
        raise UnpackError(f"RVA 0x{rva:x} is not backed by file data")


# The supplied client's unrolled XTEA-4 loop, with RIP displacements wildcarded.
# Match all four key loads and check their relationship, not a fixed file offset.
KEY_PATTERN = re.compile(
    rb"\x8b\x1e\x8b\xcb\xc1\xe9\x05\x8b\xc3\x44\x8b\x1d(.{4})"
    rb"\x8b\x7e\x04\x48\x8d\x76\x08\x44\x8b\x15(.{4})"
    rb"\x4c\x8b\x05(.{4})\x8b\x15(.{4})\xc1\xe0\x04"
    rb"\x81\xc2\x72\xf3\x6e\x3c", re.DOTALL,
)


def discover_key(data: bytes) -> dict:
    pe = PEImage(data)
    found = []
    for _, rva, raw, size, flags in pe.sections:
        if not flags & 0x20000000:  # executable section
            continue
        for match in KEY_PATTERN.finditer(data[raw:raw + size]):
            start = rva + match.start()
            refs = [start + end + struct.unpack("<i", match.group(i))[0]
                    for i, end in enumerate((16, 30, 37, 43), 1)]
            if refs != [refs[0], refs[0] + 12, refs[0] + 4, refs[0] + 8]:
                continue
            key_offset = pe.rva_to_offset(refs[0], 16)
            key = data[key_offset:key_offset + 16]
            found.append({
                "algorithm": "XTEA", "rounds": 4, "byte_order": "little",
                "key_hex": key.hex(),
                "key_words": [f"0x{x:08x}" for x in struct.unpack("<4I", key)],
                "key_rva": f"0x{refs[0]:x}", "key_file_offset": f"0x{key_offset:x}",
                "loop_rva": f"0x{start:x}",
                "client_sha256": hashlib.sha256(data).hexdigest(),
            })
    if len(found) != 1:
        raise UnpackError(f"Expected one supported XTEA-4 routine, found {len(found)}. "
                          "This client build is not supported; no offset guessing was attempted.")
    return found[0]


def decrypt_xtea4(data: bytes, key: bytes) -> bytes:
    """Little-endian XTEA ECB, four cycles (eight half-rounds), no unpadding."""
    if len(key) != 16 or len(data) % 8:
        raise UnpackError("XTEA requires a 16-byte key and aligned 8-byte blocks")
    words = struct.unpack("<4I", key)
    # Precompute the sums for the client's four unrolled cycles.
    schedule = []
    value = (DELTA * 4) & MASK
    for _ in range(4):
        right = (value + words[(value >> 11) & 3]) & MASK
        value = (value - DELTA) & MASK
        left = (value + words[value & 3]) & MASK
        schedule.append((right, left))
    result = bytearray(len(data))
    for off in range(0, len(data), 8):
        v0, v1 = struct.unpack_from("<2I", data, off)
        for right, left in schedule:
            v1 = (v1 - ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ right)) & MASK
            v0 = (v0 - ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ left)) & MASK
        struct.pack_into("<2I", result, off, v0, v1)
    return bytes(result)


def decode_entry(stream, entry: Entry, key: bytes) -> bytes:
    lz4, xxhash = dependencies()
    stream.seek(entry.data_offset)
    encrypted = stream.read(entry.stored_size)
    if len(encrypted) != entry.stored_size:
        raise UnpackError(f"Truncated payload at entry {entry.index}")
    packed = decrypt_xtea4(encrypted, key)[:entry.compressed_size]
    if entry.compressed_size == entry.original_size:
        payload = packed
    else:
        try:
            payload = lz4.decompress(packed, uncompressed_size=entry.original_size)
        except (ValueError, lz4.LZ4BlockError) as exc:
            raise UnpackError(f"LZ4 failure at entry {entry.index}: wrong key or damaged archive") from exc
    if len(payload) != entry.original_size:
        raise UnpackError(f"Size mismatch at entry {entry.index}")
    if xxhash.xxh32(payload, seed=MAGIC).intdigest() != entry.checksum:
        raise UnpackError(f"XXH32 mismatch at entry {entry.index}: wrong key or damaged archive")
    return payload


def normalize_name(name: str) -> str:
    # Match the client's ASCII tolower + backslash replacement.
    return name.replace("\\", "/").translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"))


def name_hash(name: str) -> int:
    return zlib.crc32(normalize_name(name).encode("utf-8")) & MASK


def safe_relative_name(name: str) -> Path:
    """Map virtual game drive paths, but never accept traversal or absolute paths."""
    name = normalize_name(name)
    if re.match(r"^[a-z]:/", name):
        name = "_drives/" + name[0] + "/" + name[3:]
    parts = name.split("/")
    reserved = {"con", "prn", "aux", "nul"} | {f"{s}{i}" for s in ("com", "lpt") for i in range(1, 10)}
    if (not name or len(name) > 1024 or any(
        part in ("", ".", "..") or len(part) > 240 or part.endswith((" ", "."))
        or part.split(".")[0] in reserved or re.search(r'[<>:"|?*\x00-\x1f\x7f]', part)
        for part in parts
    )):
        raise UnpackError(f"Unsafe archive filename: {name!r}")
    return Path(*parts)


# Filename references (including drive paths) and Python imports are hints only:
# a candidate is accepted ONLY if its CRC32 exists in the archive index.
PATH_PATTERN = re.compile(
    rb"[A-Za-z0-9_./:\\ -]{1,240}\.(?:pyc|pyo|py|msm|msa|mse|msf|txt|xml|json|cfg|ini|"
    rb"sub|dds|tga|png|jpg|jpeg|bmp|psd|gr2|wav|mp3|ogg|avi|ttf|otf|def|bin|dat|sct|atr|raw|wtr)\b",
    re.IGNORECASE,
)
IMPORT_PATTERN = re.compile(rb"(?m)^\s*(?:from|import)[ \t]+([A-Za-z_][A-Za-z0-9_.]*(?:[ \t]*,[ \t]*[A-Za-z_][A-Za-z0-9_.]*)*)")
DIRECTORY_PATTERN = re.compile(rb'''["']([A-Za-z0-9_./:\\ -]{1,200}[/\\])["']''')
ASSIGNMENT_PATTERN = re.compile(rb"(?m)^[ \t]*((?:self\.)?[A-Za-z_]\w*)[ \t]*=[ \t]*([^\r\n]{1,1024})")
STRING_TOKEN = r'''(?:"[A-Za-z0-9_./:\\ -]{0,240}"|'[A-Za-z0-9_./:\\ -]{0,240}'|(?:self\.)?[A-Za-z_]\w*)'''
STRING_EXPRESSION = re.compile(STRING_TOKEN + r"(?:\s*\+\s*" + STRING_TOKEN + r")*")


def static_string_hints(data: bytes):
    """Recognize only literal/name concatenations, never eval/exec/import code."""
    values = {}
    for match in ASSIGNMENT_PATTERN.finditer(data):
        if len(values) >= 2048:
            break
        expression = match.group(2).decode("ascii", errors="replace").split("#", 1)[0].strip()
        if not STRING_EXPRESSION.fullmatch(expression):
            continue
        parts = []
        for token in re.findall(STRING_TOKEN, expression):
            if token.startswith(('"', "'")):
                parts.append(token[1:-1])
            elif token in values:
                parts.append(values[token])
            else:
                break
        else:
            value = "".join(parts)
            if len(value) <= 1024:
                values[match.group(1).decode("ascii")] = value
                yield value


class NameResolver:
    def __init__(self, hashes):
        self.hashes = set(hashes)
        self.matches: dict[int, set[str]] = {}

    def add(self, name: str):
        name = normalize_name(name.strip())
        hashed = name_hash(name)
        if hashed not in self.hashes:
            return
        try:
            safe_relative_name(name)
        except UnpackError:
            return
        self.matches.setdefault(hashed, set()).add(name)

    def scan(self, data: bytes):
        fragments = set()
        for match in PATH_PATTERN.finditer(data):
            text = match.group().decode("ascii").strip()
            # Whitespace may be part of a virtual path ("ymir work") or the
            # preceding source code. Also try path suffixes and the basename.
            starts = {0} | {i + 1 for i, char in enumerate(text) if char in " /\\"}
            for start in starts:
                candidate = text[start:]
                self.add(candidate)
                if len(fragments) < 2048:
                    fragments.add(candidate)
        for match in IMPORT_PATTERN.finditer(data):
            for part in match.group(1).decode("ascii").split(","):
                module = part.strip().replace(".", "/")
                self.add(module + ".py")
                self.add(module + ".pyc")
                self.add(module + "/__init__.py")
        # Static hints for PATH + "image.png". This never evaluates Python.
        # Bound both sets to prevent combinatorial work on arbitrary input.
        directories = set()
        for value in static_string_hints(data):
            self.add(value)
            if value.endswith(("/", "\\")) and len(directories) < 128:
                directories.add(value)
        for match in DIRECTORY_PATTERN.finditer(data):
            if len(directories) >= 128:
                break
            directories.add(match.group(1).decode("ascii"))
        for directory in sorted(directories):
            for fragment in sorted(fragments):
                self.add(directory + fragment)

    def load(self, path: Path):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                self.add(line)

    def resolved(self, hashed: int) -> str | None:
        names = self.matches.get(hashed, set())
        return next(iter(names)) if len(names) == 1 else None


def progress(done: int, total: int):
    if done % 100 == 0 or done == total:
        print(f"Verified {done}/{total}", file=sys.stderr)


def process_archive(archive: Path, entries: list[Entry], key_info: dict,
                    resolver: NameResolver, output: Path | None) -> dict:
    """Verify all records; publish a fresh output directory only after success."""
    key = bytes.fromhex(key_info["key_hex"])
    summary = {"archive": str(archive), "files": len(entries),
               "original_bytes": sum(e.original_size for e in entries),
               "client_sha256": key_info["client_sha256"]}
    if output is None:
        with archive.open("rb") as stream:
            for entry in entries:
                decode_entry(stream, entry, key)
                progress(entry.index + 1, len(entries))
        return {**summary, "verified": len(entries)}
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise UnpackError(f"Output already exists (never overwritten): {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".alt2-unpack-", dir=output.parent) as temp:
        stage = Path(temp)
        spool = stage / "spool"
        spool.mkdir()
        result = stage / "result"
        result.mkdir()
        digests = []
        with archive.open("rb") as stream:
            for entry in entries:
                data = decode_entry(stream, entry, key)
                digests.append(hashlib.sha256(data).hexdigest())
                (spool / str(entry.index)).write_bytes(data)
                resolver.scan(data)
                progress(entry.index + 1, len(entries))
        records = []
        known = 0
        # Namespaces keep unknown files and metadata separate from game paths.
        for entry, digest in zip(entries, digests):
            name = resolver.resolved(entry.name_hash)
            relative = (Path("files") / safe_relative_name(name) if name else
                        Path("unknown") / f"{entry.index:04d}_{entry.name_hash:08x}.bin")
            target = result / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise UnpackError(f"Duplicate output path: {relative}")
            (spool / str(entry.index)).rename(target)
            known += name is not None
            records.append({**asdict(entry), "name_hash_hex": f"{entry.name_hash:08x}",
                            "name": name, "candidates": sorted(resolver.matches.get(entry.name_hash, [])),
                            "output": relative.as_posix(), "sha256": digest})
        summary.update(verified=len(entries), named=known, unknown=len(entries) - known)
        manifest = {**summary, "format": "ALT2/XTEA-4/LZ4/XXH32", "entries": records}
        (result / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if output.exists() or output.is_symlink():
            raise UnpackError("Output appeared during extraction; refusing to overwrite it")
        result.rename(output)
    return {**summary, "output": str(output)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    key = commands.add_parser("key", help="Locate the XTEA key statically in the client")
    key.add_argument("--client", type=Path, default=HERE / "metin2client.exe")
    for command in ("list", "verify", "extract"):
        sub = commands.add_parser(command, help={"list": "List headers without decrypting payloads",
                                                "verify": "Decrypt and validate all files without saving",
                                                "extract": "Decrypt, validate, and recover filenames"}[command])
        sub.add_argument("archive", nargs="?", type=Path, default=HERE / "data" / "root")
        sub.add_argument("--client", type=Path, default=HERE / "metin2client.exe")
        sub.add_argument("--names", type=Path, action="append", default=[], help="UTF-8 filename list, one per line; repeatable")
        sub.add_argument("--max-file-size", type=int, default=DEFAULT_FILE_LIMIT, metavar="BYTES")
        sub.add_argument("--max-total-size", type=int, default=DEFAULT_TOTAL_LIMIT, metavar="BYTES")
        if command == "extract":
            sub.add_argument("-o", "--output", type=Path, default=HERE / "unpacked" / "root", help="New directory; existing output is never overwritten")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        client = args.client.read_bytes()
        if args.command == "key":
            print(json.dumps(discover_key(client), indent=2))
            return 0
        if args.max_file_size <= 0 or args.max_total_size <= 0:
            raise UnpackError("Size limits must be positive")
        entries = read_index(args.archive, args.max_file_size, args.max_total_size)
        resolver = NameResolver(e.name_hash for e in entries)
        resolver.scan(client)
        for path in args.names:
            resolver.load(path)
        if args.command == "list":
            print("INDEX\tNAME_HASH\tORIGINAL\tCOMPRESSED\tSTORED\tNAME (unverified payload)")
            for entry in entries:
                print(f"{entry.index}\t{entry.name_hash:08x}\t{entry.original_size}\t"
                      f"{entry.compressed_size}\t{entry.stored_size}\t{resolver.resolved(entry.name_hash) or '-'}")
            return 0
        info = discover_key(client)
        dependencies()
        summary = process_archive(args.archive, entries, info, resolver,
                                  args.output if args.command == "extract" else None)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    except (UnpackError, OSError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Cancelled; incomplete output was not published.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
