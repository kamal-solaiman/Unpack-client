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
from dataclasses import asdict, dataclass
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
    # Convenience classification for unknown/ output only, never a recovered filename.
    if data.startswith(b"\x03\xf3\r\n"):
        return ".pyc"  # CPython 2.7 bytecode; never execute it
    if data.startswith((b"#", b"import ", b"from ", b"\r\n", b"\n")):
        return ".py"  # best-effort; use the manifest for authoritative metadata
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
    rb"[A-Za-z0-9_./:\\ -]{1,240}\.(?:markdown|md|pyc|pyo|py|msm|msa|mse|msf|txt|xml|json|cfg|ini|"
    rb"sub|dds|tga|png|jpg|jpeg|bmp|psd|gr2|wav|mp3|ogg|avi|ttf|otf|def|bin|dat|sct|atr|raw|wtr)",
    re.IGNORECASE,
)
IMPORT_PATTERN = re.compile(
    rb"(?m)^\s*(?:from|import)[ \t]+([A-Za-z_][A-Za-z0-9_.]*(?:[ \t]*,[ \t]*[A-Za-z_][A-Za-z0-9_.]*)*)")
DIRECTORY_PATTERN = re.compile(rb"""["']([A-Za-z0-9_./:\\ -]{1,200}[/\\])["']""")
ASSIGNMENT_PATTERN = re.compile(rb"(?m)^[ \t]*((?:self\.)?[A-Za-z_]\w*)[ \t]*=[ \t]*([^\r\n]{1,1024})")
STRING_TOKEN = r'''(?:"[A-Za-z0-9_./:\\ -]{0,240}"|'[A-Za-z0-9_./:\\ -]{0,240}'|(?:self\.)?[A-Za-z_]\w*)'''
STRING_EXPRESSION = re.compile(STRING_TOKEN + r"(?:\s*\+\s*" + STRING_TOKEN + r")*")
MAX_FRAGMENTS = 2048
MAX_DIRECTORIES = 128
MAX_HINTS = 2048


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

    def finalize(self) -> None:
        """Join collected directories with collected path fragments, once."""
        for directory in sorted(self.directories):
            for fragment in sorted(self.fragments):
                self.add(directory + fragment)

    def load(self, path: Path) -> None:
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                self.add(line)

    def resolved(self, hashed: int) -> str | None:
        names = self.matches.get(hashed, set())
        return next(iter(names)) if len(names) == 1 else None


def build_resolver(entries: list[Entry], client: Path | None = None,
                   name_files=()) -> NameResolver:
    """Hints from History2.exe, History/names.txt, and explicit --names lists."""
    resolver = NameResolver(e.name_hash for e in entries)
    default_names = HERE / "names.txt"
    files = list(name_files)
    if default_names.is_file() and default_names not in files:
        files.insert(0, default_names)
    for path in files:
        resolver.load(path)
    if client is not None and client.is_file():
        resolver.scan(client.read_bytes())
    return resolver


def derive_sibling_names(resolver: NameResolver, entries: list[Entry], spool: Path) -> None:
    """Python source/bytecode pairs usually share a stem: foo.py <-> foo.pyc.
    Derive one side from the other; each guess still must match the CRC32."""
    for _ in range(10):
        progressed = False
        for entry in entries:
            if resolver.resolved(entry.name_hash) is not None:
                continue
            data = (spool / str(entry.index)).read_bytes()
            is_pyc = data.startswith(b"\x03\xf3\r\n")
            for sib_index in (entry.index - 1, entry.index + 1):
                if not 0 <= sib_index < len(entries):
                    continue
                sibling = resolver.resolved(entries[sib_index].name_hash)
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


def run(path: Path, output: Path | None, max_file_size: int, max_total_size: int,
        resolver: NameResolver | None = None) -> tuple[int, int, int]:
    """Verify every entry; with an output directory also restore real names.

    Returns (entry count, decoded bytes, named file count). Output is staged
    in a temporary directory and published only after every entry succeeds.
    """
    key, iv, entries = read_index(path, max_file_size, max_total_size)
    if resolver is None:
        resolver = NameResolver(e.name_hash for e in entries)
    if output is not None:
        if output.exists() or output.is_symlink():
            raise UnpackError(f"Output already exists: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.parent.is_dir():
            raise UnpackError(f"Output parent is not a directory: {output.parent}")
    temp: Path | None = None
    named = 0
    try:
        if output is None:
            with path.open("rb") as src:
                for entry in entries:
                    decode(src, entry, key, iv)
        else:
            temp = Path(tempfile.mkdtemp(prefix=".history-unpack-", dir=output.parent))
            spool = temp / ".spool"
            spool.mkdir()
            with path.open("rb") as src:
                for entry in entries:
                    data = decode(src, entry, key, iv)
                    (spool / str(entry.index)).write_bytes(data)
                    resolver.scan(data)
            resolver.finalize()
            derive_sibling_names(resolver, entries, spool)
            manifest = []
            for entry in entries:
                data = (spool / str(entry.index)).read_bytes()
                name = resolver.resolved(entry.name_hash)
                candidates = sorted(resolver.matches.get(entry.name_hash, ()))
                if name is not None:
                    relative = Path("files") / safe_relative_name(name)
                    named += 1
                else:
                    relative = Path("unknown") / f"{entry.index:04d}_{entry.name_hash:08x}{extension(data)}"
                target = temp / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    raise UnpackError(f"Duplicate output path: {relative}")
                (spool / str(entry.index)).rename(target)
                manifest.append({**asdict(entry), "checksum": f"{entry.checksum:08x}",
                                 "name_hash": f"{entry.name_hash:08x}",
                                 "name": name, "candidates": candidates,
                                 "output": relative.as_posix(),
                                 "sha256": hashlib.sha256(data).hexdigest()})
            spool.rmdir()
            (temp / "manifest.json").write_text(json.dumps({
                "archive": str(path.resolve()), "format": "History d2 / AES-256-CFB / raw LZ4 / XXH32",
                "note": "files/ holds CRC32-verified original names; unknown/ holds "
                        "verified content whose name had no unique matching candidate.",
                "named": named, "unknown": len(entries) - named,
                "entries": manifest,
            }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            if output.exists() or output.is_symlink():
                raise UnpackError(f"Output appeared during extraction: {output}")
            temp.rename(output)
            temp = None
    finally:
        if temp is not None:
            shutil.rmtree(temp)
    return len(entries), sum(e.original_size for e in entries), named


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
    parser.add_argument("--max-file-size", type=int, default=DEFAULT_FILE_LIMIT)
    parser.add_argument("--max-total-size", type=int, default=DEFAULT_TOTAL_LIMIT)
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
        for archive, out in zip(archives, outputs):
            key, iv, entries = read_index(archive, args.max_file_size, args.max_total_size)
            if args.command == "key":
                if len(archives) > 1:
                    print(f"Archive: {archive}")
                print("History2.exe SHA-256:", client_fingerprint(args.client))
                print("The client reads a 64-byte key/IV preamble from the .d2 header; "
                      "this archive uses no additional client-side XOR masks.")
                print("Archive AES-256 key (offset 0x04):", key.hex())
                print("Archive IV material (offset 0x24):", iv.hex())
                print("AES-CFB IV used (first 16 bytes):", iv[:16].hex())
                print("Checking first entry:", end=" ")
                with archive.open("rb") as src:
                    decode(src, entries[0], key, iv)
                print("XXH32 verified")
            elif args.command == "list":
                resolver = build_resolver(entries, args.client, args.names)
                resolver.finalize()
                named = 0
                print("index  name_hash  original  stored  data_offset  name")
                for entry in entries:
                    name = resolver.resolved(entry.name_hash)
                    named += name is not None
                    print(f"{entry.index:5d}  {entry.name_hash:08x}  {entry.original_size:8d}  "
                          f"{entry.stored_size:6d}  0x{entry.data_offset:08x}  {name or '-'}")
                print(f"{len(entries)} entries; {named} names from client/name-list hints "
                      "(extract recovers more from payload contents)")
            else:
                resolver = (build_resolver(entries, args.client, args.names)
                            if out is not None else None)
                count, total, named = run(archive, out, args.max_file_size,
                                          args.max_total_size, resolver=resolver)
                print(f"Verified {count}/{count} entries ({total:,} decoded bytes)")
                if out is not None:
                    print(f"Extracted to {out} ({named} named, {count - named} unknown)")
        return 0
    except (UnpackError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Cancelled; incomplete output was not published.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
