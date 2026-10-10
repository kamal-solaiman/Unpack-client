#!/usr/bin/env python3
"""Read-only extractor for the supplied History .d2 packs. Never runs the client.

The archive embeds its key and IV; the matching client defines their use (see
FORMAT.md). name_hash is CRC32 of the virtual filename: original names and
folder paths are restored from candidates that reproduce each entry's hash
exactly. A directory argument (default: History/pack) selects among several
packs, asking whether to unpack a specific pack or all of them.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys
import tempfile
import zlib

HERE = Path(__file__).resolve().parent
MAGIC = 0xF00FED5C
MASK = 0xFFFFFFFF
HEADER = struct.Struct("<5I")
FIRST_ENTRY = 0x44
CLIENT_SHA256 = "a5b8787ff8478028c19dfce124f5f9dec8e07b333abf875e95f54b67d9c8fd3a"
DEFAULT_FILE_LIMIT = 128 * 1024 * 1024
DEFAULT_TOTAL_LIMIT = 1024 * 1024 * 1024
# Recovery scan window: how far past a corrupt header --keep-going looks for
# the next plausible entry header before giving up on the rest of the archive.
RESYNC_WINDOW = 4 * 1024 * 1024
MAX_BROKEN_REPORT = 20
VERBS = {"key": "Use", "list": "List", "verify": "Verify", "extract": "Extract"}


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


@dataclass(frozen=True)
class BrokenRecord:
    """A record header that failed validation; positions keep archive order."""
    index: int
    header_offset: int
    raw: tuple[int, int, int, int, int] | None  # None when the header itself is cut off
    error: str


@dataclass
class IndexResult:
    key: bytes
    iv: bytes
    entries: list[Entry] = field(default_factory=list)
    broken: list[BrokenRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def records(self) -> int:
        return len(self.entries) + len(self.broken)


def _header_looks_valid(buf: bytes, pos: int, size: int, max_file_size: int) -> bool:
    """Cheap plausibility check used when re-syncing after a corrupt header."""
    if pos < 0 or pos + HEADER.size > size:
        return False
    original_size, _checksum, data_offset, stored_size, _name_hash = HEADER.unpack_from(buf, pos)
    return (0 < original_size <= max_file_size and 0 < stored_size <= max_file_size
            and data_offset == pos + HEADER.size and data_offset + stored_size <= size)


def _resync(buf: bytes, start: int, size: int, max_file_size: int) -> int | None:
    """Scan forward for the next plausible header, confirmed by its successor.

    A candidate is accepted only when the record after it is also plausible
    (or it ends exactly at EOF), so random payload bytes rarely false-sync.
    Returns the header offset, or None when nothing plausible was found.
    """
    end = min(size - HEADER.size + 1, start + RESYNC_WINDOW)
    pos = start
    while pos < end:
        if _header_looks_valid(buf, pos, size, max_file_size):
            _o, _c, data_offset, stored_size, _h = HEADER.unpack_from(buf, pos)
            nxt = data_offset + stored_size
            if nxt == size or _header_looks_valid(buf, nxt, size, max_file_size):
                return pos
            # A lone plausible-looking header with no valid successor is
            # likely a false sync; keep scanning instead of accepting it.
        pos += 1
    return None


def _describe_header(offset: int, fields: tuple[int, int, int, int, int]) -> str:
    original_size, checksum, data_offset, stored_size, name_hash = fields
    return (f"header at 0x{offset:x}: original_size={original_size} checksum={checksum:08x} "
            f"data_offset=0x{data_offset:x} stored_size={stored_size} name_hash={name_hash:08x}")


def read_index_full(path: Path, max_file_size: int = DEFAULT_FILE_LIMIT,
                    max_total_size: int = DEFAULT_TOTAL_LIMIT,
                    keep_going: bool = False) -> IndexResult:
    """Read the 68-byte preamble and walk the 20-byte headers.

    Strict mode (default) raises on the first bad record, describing the raw
    field values and offsets so truncation vs. corruption can be told apart.
    With keep_going=True, bad records are collected as BrokenRecord items and
    the walker re-syncs to the next plausible header, so every salvageable
    entry before and after the damage is still recovered.
    """
    size = path.stat().st_size
    if size < FIRST_ENTRY:
        raise UnpackError(f"Truncated archive header ({size} bytes, need {FIRST_ENTRY})")
    with path.open("rb") as src:
        preamble = src.read(FIRST_ENTRY)
        if struct.unpack_from("<I", preamble)[0] != MAGIC:
            raise UnpackError("Not a History .d2 archive (bad magic)")
        key, iv = preamble[4:36], preamble[36:68]
        if keep_going:
            # Whole-file buffer so re-sync scans use absolute file offsets.
            src.seek(0)
            buf = src.read()
        else:
            buf = b""
        result = IndexResult(key=key, iv=iv)
        offset = FIRST_ENTRY
        total = 0
        record = 0
        while offset < size:
            if size - offset < HEADER.size:
                error = (f"truncated entry header at 0x{offset:x} "
                         f"(only {size - offset} of {HEADER.size} bytes remain; "
                         f"archive ends at 0x{size:x}, likely an incomplete download)")
                if not keep_going:
                    raise UnpackError(f"Record {record}: {error}")
                result.broken.append(BrokenRecord(record, offset, None, error))
                break
            if keep_going:
                fields = HEADER.unpack_from(buf, offset)
            else:
                src.seek(offset)
                fields = HEADER.unpack(src.read(HEADER.size))
            original_size, checksum, data_offset, stored_size, name_hash = fields
            detail = _describe_header(offset, fields)
            if original_size == checksum == data_offset == stored_size == name_hash == 0:
                note = (f"Record {record}: all-zero header at 0x{offset:x} "
                        f"({'end of archive' if offset + HEADER.size >= size else 'stopping here'}; "
                        f"{size - offset - HEADER.size} trailing bytes ignored)")
                if keep_going:
                    result.warnings.append(note + " (treated as end-of-archive terminator)")
                    break
                raise UnpackError(note + " — re-run with --keep-going to extract the entries before it")
            if data_offset != offset + HEADER.size:
                error = (f"invalid payload offset in record {record}: {detail} "
                         f"(expected data_offset 0x{offset + HEADER.size:x})")
                if not keep_going:
                    raise UnpackError(error + " — re-run with --keep-going to salvage the readable entries")
                # A forward gap with otherwise sane sizes is likely padding:
                # skip the gap with a warning instead of dropping the entry.
                if (data_offset > offset + HEADER.size and 0 < original_size <= max_file_size
                        and 0 < stored_size <= max_file_size and data_offset + stored_size <= size):
                    result.warnings.append(
                        f"Record {record}: skipped {data_offset - offset - HEADER.size} "
                        f"padding bytes at 0x{offset + HEADER.size:x}")
                else:
                    result.broken.append(BrokenRecord(record, offset, fields, error))
                    record += 1
                    found = _resync(buf, offset + 1, size, max_file_size)
                    if found is None:
                        result.warnings.append(
                            f"No further plausible headers after 0x{offset:x}; "
                            f"stopped with {size - offset} unread bytes")
                        break
                    result.warnings.append(f"Re-synced at 0x{found:x} after record {record - 1}")
                    offset = found
                    continue
            if not stored_size or not original_size:
                error = (f"zero size in record {record}: {detail} "
                         f"(possible terminator record or corrupt header)")
                if not keep_going:
                    raise UnpackError(error + " — re-run with --keep-going to salvage the readable entries")
                result.broken.append(BrokenRecord(record, offset, fields, error))
                record += 1
                found = _resync(buf, offset + 1, size, max_file_size)
                if found is None:
                    result.warnings.append(
                        f"No further plausible headers after 0x{offset:x}; "
                        f"stopped with {size - offset} unread bytes")
                    break
                result.warnings.append(f"Re-synced at 0x{found:x} after record {record - 1}")
                offset = found
                continue
            if data_offset + stored_size > size:
                error = (f"truncated payload in record {record}: {detail} "
                         f"(payload ends at 0x{data_offset + stored_size:x} "
                         f"but the file is only 0x{size:x} bytes; likely an incomplete download)")
                if not keep_going:
                    raise UnpackError(error + " — re-run with --keep-going to extract the entries before it")
                result.broken.append(BrokenRecord(record, offset, fields, error))
                record += 1
                found = _resync(buf, offset + 1, size, max_file_size)
                if found is None:
                    result.warnings.append(
                        f"No further plausible headers after 0x{offset:x}; "
                        f"stopped with {size - offset} unread bytes")
                    break
                result.warnings.append(f"Re-synced at 0x{found:x} after record {record - 1}")
                offset = found
                continue
            total += original_size
            if (original_size > max_file_size or stored_size > max_file_size
                    or total > max_total_size):
                raise UnpackError(
                    f"Size safety limit exceeded in record {record}: {detail} "
                    f"(raise --max-file-size/--max-total-size for trusted large packs)")
            result.entries.append(Entry(record, offset, original_size, checksum,
                                        data_offset, stored_size, name_hash))
            record += 1
            if record > 1_000_000:
                raise UnpackError("Too many entries")
            offset = data_offset + stored_size
    if not result.entries and not result.broken:
        raise UnpackError("Archive has no entries")
    return result


def read_index(path: Path, max_file_size: int = DEFAULT_FILE_LIMIT,
               max_total_size: int = DEFAULT_TOTAL_LIMIT) -> tuple[bytes, bytes, list[Entry]]:
    """Strict index read; see read_index_full() for the recovering variant."""
    result = read_index_full(path, max_file_size, max_total_size, keep_going=False)
    return result.key, result.iv, result.entries


def decode(src, entry: Entry, key: bytes, iv: bytes) -> bytes:
    AES, lz4_block, xxhash = dependencies()
    where = f"entry {entry.index} (header at 0x{entry.header_offset:x}, payload at 0x{entry.data_offset:x})"
    src.seek(entry.data_offset)
    ciphertext = src.read(entry.stored_size)
    if len(ciphertext) != entry.stored_size:
        raise UnpackError(f"Truncated payload in {where}: file shrank or is being modified")
    # Crypto++ CFB_DecryptionTemplate uses full AES blocks (128-bit feedback).
    plaintext = AES.new(key, AES.MODE_CFB, iv=iv[:16], segment_size=128).decrypt(ciphertext)
    if entry.stored_size == entry.original_size:
        decoded = plaintext
    else:
        try:
            decoded = lz4_block.decompress(plaintext, uncompressed_size=entry.original_size)
        except (lz4_block.LZ4BlockError, ValueError, OverflowError) as exc:
            raise UnpackError(f"LZ4 decode failed in {where}: {exc}") from exc
    if len(decoded) != entry.original_size:
        raise UnpackError(f"Size mismatch in {where}: got {len(decoded)}, expected {entry.original_size}")
    if xxhash.xxh32(decoded, seed=MAGIC).intdigest() != entry.checksum:
        raise UnpackError(f"XXH32 mismatch in {where}: wrong key or corrupt archive")
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


def _is_text_like(sample: bytes) -> bool:
    if not sample or b"\x00" in sample:
        return False
    text_chars = sum(1 for byte in sample
                     if byte in (9, 10, 13) or 32 <= byte <= 126 or byte >= 128)
    return text_chars / len(sample) >= 0.90


def _looks_like_python(head: bytes, sample: bytes) -> bool:
    if head.startswith((b"#", b"import ", b"from ", b"def ", b"class ",
                        b'"""', b"'''", b"@", b"\r\n", b"\n")):
        return True
    # Assignment/docstring-led modules (e.g. BTN = "..." or indented code).
    first_lines = sample.split(b"\n", 4)[:4]
    joined = b"\n".join(first_lines)
    markers = (b"import ", b"from ", b"def ", b"class ", b"print", b"if __name__",
               b"self.", b"True", b"False", b"None", b"lambda ", b"return ")
    return any(marker in joined for marker in markers)


def extension(data: bytes) -> str:
    # Convenience classification for unknown/ output only, never a recovered filename.
    if data.startswith(b"\x03\xf3\r\n"):
        return ".pyc"  # CPython 2.7 bytecode; never execute it
    # Images.
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if data.startswith(b"BM"):
        return ".bmp"
    if data.startswith(b"DDS "):
        return ".dds"
    if data.startswith(b"\x00\x00\x01\x00"):
        return ".ico"
    if len(data) >= 26 and b"TRUEVISION-XFILE" in data[-26:]:
        return ".tga"
    # Audio / video.
    if data.startswith(b"OggS"):
        return ".ogg"
    if data.startswith(b"ID3") or (len(data) > 2 and data[0] == 0xFF
                                   and data[1] in (0xE2, 0xE3, 0xF1, 0xF2, 0xF3, 0xFA, 0xFB)):
        return ".mp3"
    if data.startswith(b"RIFF") and len(data) >= 12:
        form = data[8:12]
        if form == b"WAVE":
            return ".wav"
        if form == b"AVI ":
            return ".avi"
        if form == b"WEBP":
            return ".webp"
    # Text formats.
    sample = data[:4096]
    if _is_text_like(sample):
        head = sample.lstrip(b"\xef\xbb\xbf \t\r\n")  # BOM + leading whitespace
        if head.startswith(b"<?xml"):
            return ".xml"
        if (head.startswith(b"<") and len(head) > 1
                and (head[1:2].isalpha() or head[1:2] in (b"!", b"?"))):
            return ".xml"
        if head.startswith((b"{", b"[")):
            return ".json"
        if _looks_like_python(head, sample):
            return ".py"  # best-effort; use the manifest for authoritative metadata
        return ".txt"
    return ".bin"


# ---------------------------------------------------------------------------
# Filename recovery. Every candidate is accepted ONLY when its CRC32 equals an
# entry's name_hash; hints from the client or payloads can never rename a file
# whose hash does not match. Collisions are detected as ambiguity (see below).

def normalize_name(name: str) -> str:
    # Observed recovered names are lowercase with forward slashes; mirror that.
    return name.replace("\\", "/").translate(
        str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"))


def name_hash(name: str) -> int:
    return zlib.crc32(normalize_name(name).encode("utf-8")) & MASK


def safe_relative_name(name: str) -> Path:
    """Map a virtual path, but never accept traversal or absolute paths."""
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


# Filename references (including drive paths) and Python imports are hints only.
# Extensions are matched without a trailing word boundary so strings embedded
# in bytecode (co_filename followed by marshal data) still yield candidates;
# the CRC32 gate rejects every wrong cut.
PATH_PATTERN = re.compile(
    rb"[A-Za-z0-9_./:\\ -]{1,240}\.(?:markdown|md|rst|pyc|pyo|py|pyw|lua|msm|msa|mse|msf|sub|spr|"
    rb"dds|tga|png|jpg|jpeg|bmp|gif|tif|tiff|pcx|psd|ico|cur|ani|gr2|img|tex|atlas|"
    rb"wav|mp3|ogg|avi|mp4|m4a|flac|mid|midi|ttf|otf|fnt|txt|xml|json|yaml|yml|cfg|ini|"
    rb"lan|lst|csv|po|mo|log|html|htm|css|js|eff|mde|prt|pns|idf|lmd|fx|shader|mtrl|"
    rb"def|bin|dat|sct|atr|raw|wtr|pack|cache|db|gz|zip)",
    re.IGNORECASE,
)
IMPORT_PATTERN = re.compile(
    rb"(?m)^\s*(?:from|import)[ \t]+([A-Za-z_][A-Za-z0-9_.]*(?:[ \t]*,[ \t]*[A-Za-z_][A-Za-z0-9_.]*)*)")
DIRECTORY_PATTERN = re.compile(rb"""["']([A-Za-z0-9_./:\\ -]{1,200}[/\\])["']""")
ASSIGNMENT_PATTERN = re.compile(rb"(?m)^[ \t]*((?:self\.)?[A-Za-z_]\w*)[ \t]*=[ \t]*([^\r\n]{1,1024})")
STRING_TOKEN = r'''(?:"[A-Za-z0-9_./:\\ -]{0,240}"|'[A-Za-z0-9_./:\\ -]{0,240}'|(?:self\.)?[A-Za-z_]\w*)'''
STRING_EXPRESSION = re.compile(STRING_TOKEN + r"(?:\s*\+\s*" + STRING_TOKEN + r")*")
# Quoted references without an extension (e.g. LoadImage("icon/item/001")): the
# real entry name is usually the stem plus an asset extension, tried below.
QUOTED_STEM_PATTERN = re.compile(rb"""["']([A-Za-z0-9_./\\ -]{1,200})["']""")
STEM_EXTENSIONS = ("png", "dds", "tga", "jpg", "jpeg", "bmp", "gif", "sub", "spr",
                   "wav", "mp3", "ogg", "msm", "msa", "mse", "msf", "gr2",
                   "txt", "xml", "py", "pyc")
# Well-known roots seen in this client family; every combination must still
# pass the CRC32 gate, so wrong guesses are harmless, just slower.
KNOWN_DIRECTORIES = ("uiscript/", "locale/", "lib/", "ui/", "data/", "etc/",
                     "d:/ymir work/", "d:/ymir work/ui/", "ymir work/", "ymir work/ui/")
MAX_FRAGMENTS = 2048
MAX_DIRECTORIES = 128
MAX_HINTS = 2048
MAX_STEMS = 2048


def static_string_hints(data: bytes):
    """Recognize only literal/name concatenations, never eval/exec/import code."""
    values = {}
    for match in ASSIGNMENT_PATTERN.finditer(data):
        if len(values) >= MAX_HINTS:
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
        self.fragments: set[str] = set()
        self.directories: set[str] = set()
        self.stems: set[str] = set()

    def add(self, name: str) -> None:
        name = normalize_name(name.strip())
        if not name:
            return
        hashed = name_hash(name)
        if hashed not in self.hashes:
            return
        try:
            safe_relative_name(name)
        except UnpackError:
            return
        self.matches.setdefault(hashed, set()).add(name)

    def scan(self, data: bytes) -> None:
        for match in PATH_PATTERN.finditer(data):
            text = match.group().decode("ascii").strip()
            # Whitespace may belong to a virtual path ("ymir work") or to the
            # surrounding source; try every path suffix and the basename.
            starts = {0} | {i + 1 for i, char in enumerate(text) if char in " /\\"}
            for start in starts:
                candidate = text[start:]
                self.add(candidate)
                if len(self.fragments) < MAX_FRAGMENTS:
                    self.fragments.add(candidate)
        for match in IMPORT_PATTERN.finditer(data):
            for part in match.group(1).decode("ascii").split(","):
                module = part.strip().replace(".", "/")
                self.add(module + ".py")
                self.add(module + ".pyc")
                self.add(module + "/__init__.py")
        # Static hints for PATH + "image.png". This never evaluates Python.
        for value in static_string_hints(data):
            self.add(value)
            if value.endswith(("/", "\\")) and len(self.directories) < MAX_DIRECTORIES:
                self.directories.add(normalize_name(value))
        for match in DIRECTORY_PATTERN.finditer(data):
            if len(self.directories) >= MAX_DIRECTORIES:
                break
            self.directories.add(normalize_name(match.group(1).decode("ascii")))
        # Extension-less quoted references ("icon/item/001"): the stored name
        # is usually the stem plus an asset extension; try each (CRC32-gated).
        for match in QUOTED_STEM_PATTERN.finditer(data):
            if len(self.stems) >= MAX_STEMS:
                break
            stem = match.group(1).decode("ascii").strip()
            if not stem or "." in stem.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]:
                continue  # already has an extension; PATH_PATTERN handled it
            if "/" not in stem and "\\" not in stem and len(stem) < 4:
                continue  # single short word: more noise than signal
            stem = normalize_name(stem)
            self.stems.add(stem)
            for ext in STEM_EXTENSIONS:
                self.add(f"{stem}.{ext}")

    def finalize(self) -> None:
        """Join collected directories with collected path fragments, once."""
        directories = set(self.directories) | set(KNOWN_DIRECTORIES)
        basenames = {fragment.rsplit("/", 1)[-1] for fragment in self.fragments}
        basenames |= {stem.rsplit("/", 1)[-1] for stem in self.stems}
        for directory in sorted(directories):
            for fragment in sorted(self.fragments):
                self.add(directory + fragment)
            # Basename + directory covers dir and file seen in different places.
            for base in sorted(basenames):
                self.add(directory + base)

    def load(self, path: Path) -> None:
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                self.add(line)

    def resolved(self, hashed: int) -> str | None:
        names = self.matches.get(hashed, set())
        return next(iter(names)) if len(names) == 1 else None

    def unknown_reason(self, hashed: int) -> str:
        """Explain why an entry stayed unnamed, for the manifest."""
        candidates = self.matches.get(hashed, set())
        if not candidates:
            return ("no candidate matched this hash; the name appears neither in the "
                    "client strings nor in any payload reference — try --names with a "
                    "wordlist of expected paths")
        return (f"ambiguous: {len(candidates)} different candidates share this hash; "
                f"kept unnamed (see candidates)")


# Bounds for --hints scanning (already-extracted trees used as hint sources).
MAX_HINT_FILES = 200_000
MAX_HINT_FILE_SIZE = 64 * 1024 * 1024
MAX_HINT_TOTAL = 512 * 1024 * 1024


def scan_hint_path(resolver: NameResolver, hint: Path) -> int:
    """Scan a file or directory tree for filename hints; returns files scanned."""
    targets: list[Path] = []
    if hint.is_file():
        targets = [hint]
    elif hint.is_dir():
        for sub in sorted(hint.rglob("*")):
            if sub.is_file() and not sub.is_symlink():
                targets.append(sub)
                if len(targets) >= MAX_HINT_FILES:
                    break
    else:
        raise UnpackError(f"Hint path not found: {hint}")
    scanned = 0
    total = 0
    for target in targets:
        try:
            size = target.stat().st_size
        except OSError:
            continue
        if size > MAX_HINT_FILE_SIZE or total + size > MAX_HINT_TOTAL:
            continue
        try:
            data = target.read_bytes()
        except OSError:
            continue
        total += len(data)
        scanned += 1
        resolver.scan(data)
    return scanned


def build_resolver(entries: list[Entry], client: Path | None = None,
                   name_files=(), hint_paths=()) -> NameResolver:
    """Hints from History2.exe, History/names.txt, --names lists, --hints trees."""
    resolver = NameResolver(e.name_hash for e in entries)
    default_names = HERE / "names.txt"
    files = list(name_files)
    if default_names.is_file() and default_names not in files:
        files.insert(0, default_names)
    for path in files:
        resolver.load(path)
    if client is not None and client.is_file():
        resolver.scan(client.read_bytes())
    for hint in hint_paths:
        scan_hint_path(resolver, hint)
    return resolver


def derive_sibling_names(resolver: NameResolver, entries: list[Entry], spool: Path) -> None:
    """Python source/bytecode pairs usually share a stem: foo.py <-> foo.pyc.
    Derive one side from the other; each guess still must match the CRC32."""
    by_index = {entry.index: entry for entry in entries}
    for _ in range(10):
        progressed = False
        for entry in entries:
            if resolver.resolved(entry.name_hash) is not None:
                continue
            spooled = spool / str(entry.index)
            if not spooled.is_file():
                continue  # --keep-going: this entry failed to decode
            data = spooled.read_bytes()
            is_pyc = data.startswith(b"\x03\xf3\r\n")
            for sib_index in (entry.index - 1, entry.index + 1):
                neighbor = by_index.get(sib_index)
                if neighbor is None:
                    continue
                sibling = resolver.resolved(neighbor.name_hash)
                if not sibling:
                    continue
                if is_pyc and sibling.endswith(".py"):
                    candidate = sibling[:-3] + ".pyc"
                elif not is_pyc and sibling.endswith(".pyc"):
                    candidate = sibling[:-4] + ".py"
                else:
                    continue
                resolver.add(candidate)
                if resolver.resolved(entry.name_hash) is not None:
                    progressed = True
                    break
        if not progressed:
            break


@dataclass
class RunResult:
    total: int       # every record seen (decoded + broken + failed)
    decoded: int     # bytes successfully decoded
    named: int       # decoded entries restored to a unique name
    ok: int          # entries successfully decoded
    broken: int      # records rejected while reading the index
    failed: int      # entries whose payload failed to decode
    warnings: list[str] = field(default_factory=list)


def _run(path: Path, output: Path | None, max_file_size: int, max_total_size: int,
         resolver: NameResolver | None = None, keep_going: bool = False) -> RunResult:
    """Verify every entry; with an output directory also restore real names.

    Strict mode (default) raises on the first bad record and publishes
    nothing. With keep_going=True, bad records are recorded in the manifest
    (status broken/failed) and every salvageable entry is still published.
    """
    index = read_index_full(path, max_file_size, max_total_size, keep_going=keep_going)
    key, iv, entries = index.key, index.iv, index.entries
    warnings = list(index.warnings)
    if resolver is None:
        resolver = NameResolver(e.name_hash for e in entries)
    if output is not None:
        if output.exists() or output.is_symlink():
            raise UnpackError(f"Output already exists: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.parent.is_dir():
            raise UnpackError(f"Output parent is not a directory: {output.parent}")
    failures: dict[int, str] = {}
    decoded_bytes = 0
    temp: Path | None = None
    named = 0
    try:
        if output is None:
            with path.open("rb") as src:
                for entry in entries:
                    try:
                        data = decode(src, entry, key, iv)
                    except UnpackError as exc:
                        if not keep_going:
                            raise
                        failures[entry.index] = str(exc)
                        continue
                    decoded_bytes += len(data)
        else:
            temp = Path(tempfile.mkdtemp(prefix=".history-unpack-", dir=output.parent))
            spool = temp / ".spool"
            spool.mkdir()
            with path.open("rb") as src:
                for entry in entries:
                    try:
                        data = decode(src, entry, key, iv)
                    except UnpackError as exc:
                        if not keep_going:
                            raise
                        failures[entry.index] = str(exc)
                        continue
                    decoded_bytes += len(data)
                    (spool / str(entry.index)).write_bytes(data)
                    resolver.scan(data)
            resolver.finalize()
            derive_sibling_names(resolver, entries, spool)
            manifest = []
            for entry in entries:
                if entry.index in failures:
                    manifest.append({**asdict(entry), "checksum": f"{entry.checksum:08x}",
                                     "name_hash": f"{entry.name_hash:08x}",
                                     "status": "failed", "error": failures[entry.index],
                                     "name": None, "candidates": [], "output": None,
                                     "sha256": None})
                    continue
                data = (spool / str(entry.index)).read_bytes()
                name = resolver.resolved(entry.name_hash)
                candidates = sorted(resolver.matches.get(entry.name_hash, ()))
                row: dict = {**asdict(entry), "checksum": f"{entry.checksum:08x}",
                             "name_hash": f"{entry.name_hash:08x}",
                             "status": "ok",
                             "name": name, "candidates": candidates,
                             "sha256": hashlib.sha256(data).hexdigest()}
                if name is not None:
                    relative = Path("files") / safe_relative_name(name)
                    named += 1
                else:
                    row["unknown_reason"] = resolver.unknown_reason(entry.name_hash)
                    relative = Path("unknown") / f"{entry.index:04d}_{entry.name_hash:08x}{extension(data)}"
                row["output"] = relative.as_posix()
                target = temp / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    raise UnpackError(f"Duplicate output path: {relative}")
                (spool / str(entry.index)).rename(target)
                manifest.append(row)
            for record in index.broken:
                if record.raw is None:
                    original_size = checksum = data_offset = stored_size = name_hash = None
                else:
                    original_size, checksum, data_offset, stored_size, name_hash = record.raw
                    checksum = f"{checksum:08x}"
                    name_hash = f"{name_hash:08x}"
                manifest.append({"index": record.index, "header_offset": record.header_offset,
                                 "original_size": original_size, "checksum": checksum,
                                 "data_offset": data_offset, "stored_size": stored_size,
                                 "name_hash": name_hash, "status": "broken",
                                 "error": record.error, "name": None, "candidates": [],
                                 "output": None, "sha256": None})
            manifest.sort(key=lambda row: row["index"])
            ok_count = len(entries) - len(failures)
            spool.rmdir()
            (temp / "manifest.json").write_text(json.dumps({
                "archive": str(path.resolve()), "format": "History d2 / AES-256-CFB / raw LZ4 / XXH32",
                "note": "files/ holds CRC32-verified original names; unknown/ holds "
                        "verified content whose name had no unique matching candidate; "
                        "broken/failed rows document records that could not be recovered.",
                "named": named, "unknown": ok_count - named,
                "broken": len(index.broken), "failed": len(failures),
                "warnings": warnings,
                "entries": manifest,
            }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            if output.exists() or output.is_symlink():
                raise UnpackError(f"Output appeared during extraction: {output}")
            temp.rename(output)
            temp = None
    finally:
        if temp is not None:
            shutil.rmtree(temp)
    return RunResult(total=index.records, decoded=decoded_bytes, named=named,
                     ok=len(entries) - len(failures), broken=len(index.broken),
                     failed=len(failures), warnings=warnings)


def run(path: Path, output: Path | None, max_file_size: int, max_total_size: int,
        resolver: NameResolver | None = None, keep_going: bool = False) -> tuple[int, int, int]:
    """Strict-compatible wrapper: returns (record count, decoded bytes, named)."""
    result = _run(path, output, max_file_size, max_total_size,
                  resolver=resolver, keep_going=keep_going)
    return result.total, result.decoded, result.named


# ---------------------------------------------------------------------------
# Pack selection: the argument may be one .d2 file or a directory of packs.

def select_packs(path: Path, all_: bool = False, files=(), verb: str = "Extract",
                 interactive: bool | None = None, input_fn=input) -> list[Path]:
    """Resolve a pack file or a directory into the packs to process.

    With several packs, choose interactively ('specific pack or all?') when a
    terminal is available; scripts must pass --all or --file explicitly.
    """
    if not path.exists():
        raise UnpackError(f"Pack path not found: {path}")
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise UnpackError(f"Not a pack file or directory: {path}")
    packs = sorted(p for p in path.iterdir() if p.is_file() and p.suffix.lower() == ".d2")
    if not packs:
        raise UnpackError(f"No .d2 packs found in {path}")
    if files:
        chosen: list[Path] = []
        for spec in files:
            hits = [p for p in packs
                    if p.name.lower() == spec.lower() or p.stem.lower() == spec.lower()]
            if not hits:
                available = ", ".join(p.name for p in packs)
                raise UnpackError(f"Pack not found: {spec} (available: {available})")
            for pack in hits:
                if pack not in chosen:
                    chosen.append(pack)
        return chosen
    if all_ or len(packs) == 1:
        return packs
    if interactive is None:
        interactive = sys.stdin.isatty()
    if not interactive:
        raise UnpackError(
            f"{len(packs)} packs found in {path}; choose with --file NAME (repeatable) "
            "or process every pack with --all")
    print(f"{len(packs)} packs found:")
    for index, pack in enumerate(packs, 1):
        print(f"  [{index}] {pack.name} ({pack.stat().st_size:,} bytes)")
    while True:
        print(f"{verb} a specific pack or all? Enter a number (e.g. 1), a list (1,3), "
              "or 'a' for all: ", end="", flush=True)
        try:
            answer = input_fn()
        except (EOFError, KeyboardInterrupt) as exc:
            raise UnpackError("Pack selection cancelled") from exc
        answer = answer.strip().lower()
        if answer in ("a", "all"):
            return packs
        tokens = [t for t in re.split(r"[,\s]+", answer) if t]
        if tokens and all(t.isdigit() for t in tokens):
            chosen = []
            valid = True
            for token in tokens:
                position = int(token)
                if not 1 <= position <= len(packs):
                    valid = False
                    break
                if packs[position - 1] not in chosen:
                    chosen.append(packs[position - 1])
            if valid and chosen:
                return chosen
        print(f"Invalid choice: {answer!r} (expected a number up to {len(packs)}, or 'a')")


def output_for(pack: Path, selection_count: int, output: Path | None) -> Path:
    """One selected pack: use -o directly. Several packs: -o is their parent."""
    if selection_count == 1:
        return output if output is not None else HERE / "unpacked" / pack.stem
    base = output if output is not None else HERE / "unpacked"
    return base / pack.stem


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("key", "list", "verify", "extract"))
    parser.add_argument("archive", nargs="?", type=Path, default=HERE / "pack",
                        help="a .d2 pack file, or a directory of .d2 packs "
                             "(default: History/pack)")
    parser.add_argument("--client", type=Path, default=HERE / "History2.exe",
                        help="PE build checked by 'key' and scanned for filename hints")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output directory for one pack, or the parent directory "
                             "when several packs are processed (default: History/unpacked/<name>)")
    parser.add_argument("--all", action="store_true",
                        help="Process every pack found instead of asking")
    parser.add_argument("--file", dest="files", action="append", metavar="NAME", default=[],
                        help="Process this pack from a directory (repeatable)")
    parser.add_argument("--names", type=Path, action="append", default=[],
                        help="UTF-8 filename list, one per line; repeatable")
    parser.add_argument("--hints", type=Path, action="append", default=[],
                        help="extra file or directory scanned for filename hints "
                             "(e.g. an already-extracted pack); repeatable")
    parser.add_argument("--max-file-size", type=int, default=DEFAULT_FILE_LIMIT)
    parser.add_argument("--max-total-size", type=int, default=DEFAULT_TOTAL_LIMIT)
    parser.add_argument("--keep-going", action="store_true",
                        help="salvage readable entries from damaged/truncated packs: bad "
                             "records are recorded (broken/failed) instead of aborting, "
                             "and every recoverable file is still extracted")
    args = parser.parse_args(argv)
    try:
        if min(args.max_file_size, args.max_total_size) <= 0:
            raise UnpackError("Size limits must be positive")
        archives = select_packs(args.archive, all_=args.all, files=args.files,
                                verb=VERBS[args.command], input_fn=input)
        outputs: list[Path | None] = []
        if args.command == "extract":
            outputs = [output_for(pack, len(archives), args.output) for pack in archives]
            for out in outputs:
                if out.exists() or out.is_symlink():
                    raise UnpackError(f"Output already exists: {out}")
        else:
            outputs = [None] * len(archives)
        incomplete = False
        for archive, out in zip(archives, outputs):
            try:
                index = read_index_full(archive, args.max_file_size, args.max_total_size,
                                        keep_going=args.keep_going)
            except UnpackError as exc:
                if not args.keep_going:
                    raise
                print(f"{archive}: index unreadable: {exc}", file=sys.stderr)
                incomplete = True
                continue
            key, iv, entries = index.key, index.iv, index.entries
            for warning in index.warnings[:MAX_BROKEN_REPORT]:
                print(f"warning: {warning}")
            if len(index.warnings) > MAX_BROKEN_REPORT:
                print(f"warning: ... and {len(index.warnings) - MAX_BROKEN_REPORT} more "
                      f"(see manifest.json)")
            if args.command == "key":
                if len(archives) > 1:
                    print(f"Archive: {archive}")
                print("History2.exe SHA-256:", client_fingerprint(args.client))
                print("The client reads a 64-byte key/IV preamble from the .d2 header; "
                      "this archive uses no additional client-side XOR masks.")
                print("Archive AES-256 key (offset 0x04):", key.hex())
                print("Archive IV material (offset 0x24):", iv.hex())
                print("AES-CFB IV used (first 16 bytes):", iv[:16].hex())
                if not entries:
                    print("No readable entries in this archive.")
                    incomplete = True
                    continue
                print("Checking first readable entry:", end=" ")
                try:
                    with archive.open("rb") as src:
                        decode(src, entries[0], key, iv)
                except UnpackError as exc:
                    if not args.keep_going:
                        raise
                    print(f"FAILED: {exc}")
                    incomplete = True
                    continue
                print("XXH32 verified")
                if index.broken:
                    print(f"note: {len(index.broken)} record(s) failed index validation; "
                          f"re-run list/verify/extract with --keep-going for details")
                    incomplete = True
            elif args.command == "list":
                resolver = build_resolver(entries, args.client, args.names, args.hints)
                resolver.finalize()
                named = 0
                print("index  name_hash  original  stored  data_offset  name")
                for entry in entries:
                    name = resolver.resolved(entry.name_hash)
                    named += name is not None
                    print(f"{entry.index:5d}  {entry.name_hash:08x}  {entry.original_size:8d}  "
                          f"{entry.stored_size:6d}  0x{entry.data_offset:08x}  {name or '-'}")
                for record in index.broken[:MAX_BROKEN_REPORT]:
                    print(f"{record.index:5d}  BROKEN    {record.error}")
                if len(index.broken) > MAX_BROKEN_REPORT:
                    print(f"  ... and {len(index.broken) - MAX_BROKEN_REPORT} more broken records")
                print(f"{index.records} records ({len(entries)} readable, "
                      f"{len(index.broken)} broken); {named} names from client/name-list hints "
                      "(extract recovers more from payload contents)")
                if index.broken:
                    incomplete = True
            else:
                resolver = (build_resolver(entries, args.client, args.names, args.hints)
                            if out is not None else None)
                try:
                    result = _run(archive, out, args.max_file_size,
                                  args.max_total_size, resolver=resolver,
                                  keep_going=args.keep_going)
                except UnpackError as exc:
                    if not args.keep_going:
                        raise
                    # Fatal for this pack (no readable records at all, size
                    # limits, ...): report it and continue with the next pack.
                    print(f"{archive}: FAILED: {exc}", file=sys.stderr)
                    incomplete = True
                    continue
                print(f"Verified {result.ok}/{result.total} entries "
                      f"({result.decoded:,} decoded bytes)")
                if result.broken or result.failed:
                    print(f"  ({result.broken} broken records, {result.failed} failed payloads; "
                          f"details in manifest.json)")
                    incomplete = True
                if out is not None:
                    unknown = result.ok - result.named
                    print(f"Extracted to {out} ({result.named} named, {unknown} unknown)")
        if incomplete and args.keep_going:
            print("Done with warnings: some records could not be recovered; "
                  "see the messages above and manifest.json.", file=sys.stderr)
            return 1
        return 0
    except (UnpackError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Cancelled; incomplete output was not published.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
