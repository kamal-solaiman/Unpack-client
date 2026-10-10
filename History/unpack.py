#!/usr/bin/env python3
"""Read-only unpacker for the supplied History client pack (AES-256-CFB / LZ4 / XXH32).

The Windows client, the pack, and every extracted Python file are only ever read:
nothing is executed and no input file is modified. See README.md for the commands
and FORMAT.md for the container layout and the static-analysis evidence.

Unlike the ALT2 sample, this container stores its own key material in the archive
header. The client executable is still required: the tool derives the magic, the
header geometry, the cipher, the key length and the IV position from the client's
machine code instead of hardcoding them, and refuses builds it cannot prove.
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

MASK = 0xFFFFFFFF
ENTRY_HEADER = struct.Struct("<5I")  # original, checksum, data offset, stored, name hash
HERE = Path(__file__).resolve().parent
DEFAULT_ARCHIVE = HERE / "pack" / "workplace.d2"
DEFAULT_CLIENT = HERE / "History2.exe"
DEFAULT_OUTPUT = HERE / "unpacked" / "workplace"
DEFAULT_FILE_LIMIT = 128 * 1024 * 1024
DEFAULT_TOTAL_LIMIT = 1024 * 1024 * 1024
AES_BLOCK = 16
AES_KEY_LENGTHS = (16, 24, 32)

# Signatures of the routines the client uses on this container. They identify the
# algorithms; the geometry is derived from the code around them, never assumed.
XXH32_MINUS_PRIME2 = struct.pack("<I", 0x7A143589)  # -PRIME2, used as an imul constant
XXH32_PRIME1 = struct.pack("<I", 0x9E3779B1)
AES_SBOX = bytes.fromhex("637c777bf26b6fc5300167" "2bfed7ab76")
CRC32_TABLE = struct.pack("<4I", 0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA)
LZ4_TOKEN_LOOP = bytes.fromhex("0fb63e468bcfc1e904")  # token, literal-length nibble
NAME_BACKSLASH_TEST = bytes.fromhex("803c015c")        # cmp byte ptr [ecx+eax], 0x5c
NAME_BACKSLASH_FIX = bytes.fromhex("c604012f")         # mov byte ptr [ecx+eax], 0x2f
MODE_NAMES = (b"CFB\0", b"AES\0", b"FeedbackSize\0")

# push [iv]; push keylen; push [key] -- the cipher constructor's argument chain.
KEY_ARGUMENT_CHAIN = re.compile(rb"\x8d[\x46\x86](.)[\s\S]{0,8}\x50\x6a(.)\x8d[\x46\x86](.)\x50")
# push header_size; lea reg, [base+buffer]; push reg -- the ReadFile of the header.
HEADER_READ_CHAIN = re.compile(rb"\x6a(.)\x8d([\x40-\x7f])(.)([\x50-\x57])")
MASK_XOR_LOOP = re.compile(rb"\x31[\x40-\xbf].")
PUSH_IMM32 = re.compile(rb"\x68(....)", re.DOTALL)
CMP_IMM32 = re.compile(rb"\x81[\x38-\x3f](....)", re.DOTALL)
CALL_REL32 = re.compile(rb"\xe8(....)", re.DOTALL)


class UnpackError(Exception):
    """Unsupported, corrupt, or unsafe input."""


def dependencies():
    try:
        import lz4.block
        import xxhash
        from Crypto.Cipher import AES
    except ImportError as exc:
        raise UnpackError("Install dependencies: python -m pip install -r History/requirements.txt") from exc
    return lz4.block, xxhash, AES


@dataclass(frozen=True)
class Entry:
    index: int
    header_offset: int
    original_size: int
    checksum: int
    data_offset: int
    stored_size: int
    name_hash: int

    @property
    def compressed(self) -> bool:
        return self.stored_size != self.original_size


@dataclass(frozen=True)
class Layout:
    """Container geometry derived from the client's machine code."""

    magic: int
    header_size: int
    blob_offset: int
    blob_size: int
    key_offset: int
    key_length: int
    iv_offset: int
    iv_length: int
    reserved_offset: int
    reserved_length: int


class PEImage:
    """Minimal bounds-checked PE mapping, without loading executable code."""

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
            optional_magic = struct.unpack_from("<H", data, pe + 24)[0]
            if optional_magic == 0x10B:
                self.bits, base_offset = 32, pe + 24 + 28
            elif optional_magic == 0x20B:
                self.bits, base_offset = 64, pe + 24 + 24
            else:
                raise ValueError("unknown optional header magic")
            if machine not in (0x14C, 0x8664) or machine != (0x14C if self.bits == 32 else 0x8664):
                raise ValueError("machine type does not match the optional header")
            if not 1 <= count <= 96 or optional_size < 32:
                raise ValueError("invalid PE header")
            self.image_base = struct.unpack_from("<Q" if self.bits == 64 else "<I", data, base_offset)[0]
            self.sections = []
            for i in range(count):
                off = pe + 24 + optional_size + i * 40
                name, virtual_size, rva, raw_size, raw = struct.unpack_from("<8s4I", data, off)
                flags = struct.unpack_from("<I", data, off + 36)[0]
                if raw + raw_size > len(data):
                    raise ValueError("truncated PE section")
                self.sections.append((name.rstrip(b"\0"), rva, virtual_size, raw, raw_size, flags))
        except (struct.error, ValueError) as exc:
            raise UnpackError(f"Invalid client executable: {exc}") from exc

    def executable(self):
        """(section VA, section bytes) for every executable, file-backed section."""
        for _, rva, virtual_size, raw, raw_size, flags in self.sections:
            if flags & 0x20000000 and raw_size:
                yield self.image_base + rva, self.data[raw:raw + min(raw_size, virtual_size or raw_size)]

    def offset_to_va(self, offset: int) -> int | None:
        for _, rva, _, raw, raw_size, _ in self.sections:
            if raw <= offset < raw + raw_size:
                return self.image_base + rva + offset - raw
        return None

    def contains_va(self, va: int) -> bool:
        for _, rva, virtual_size, raw, raw_size, _ in self.sections:
            if raw_size and self.image_base + rva <= va < self.image_base + rva + max(virtual_size, raw_size):
                return True
        return False


def _modrm_displacement(data: bytes, index: int):
    """Decode a movups load/store with a plain [base+disp] memory operand."""
    opcode = data[index:index + 2]
    if opcode not in (b"\x0f\x10", b"\x0f\x11"):
        return None
    modrm = data[index + 2]
    mod, rm = modrm >> 6, modrm & 7
    if mod == 3 or rm == 4:  # register operand or SIB: not a simple displacement
        return None
    if mod == 0:
        return None if rm == 5 else (opcode == b"\x0f\x10", rm, 0, 3)
    if mod == 1:
        disp = data[index + 3]
        return opcode == b"\x0f\x10", rm, disp - 256 if disp >= 0x80 else disp, 4
    if index + 7 > len(data):
        return None
    return opcode == b"\x0f\x10", rm, struct.unpack_from("<i", data, index + 3)[0], 7


def _first(needle: bytes, data: bytes) -> int | None:
    found = data.find(needle)
    return None if found < 0 else found


@dataclass(frozen=True)
class ClientAnalysis:
    layout: Layout
    landmarks: dict
    client_sha256: str

    def to_dict(self) -> dict:
        return {"client_sha256": self.client_sha256, "layout": asdict(self.layout),
                "cipher": f"AES-{self.layout.key_length * 8}-CFB (full-block feedback)",
                "compression": "raw LZ4 block (skipped when stored_size == original_size)",
                "checksum": "XXH32 of the decoded payload, seeded with the archive magic",
                "name_hash": "CRC32 of the name after ASCII tolower and '\\' -> '/'",
                "landmarks": self.landmarks}


def analyze_client(data: bytes) -> ClientAnalysis:
    """Derive the container geometry from the client; reject builds we cannot prove."""
    pe = PEImage(data)
    code = [(va, chunk) for va, chunk in pe.executable()]
    if not code:
        raise UnpackError("The client has no executable section")

    # 1. XXH32: the round loop multiplies by -PRIME2 and PRIME1 within a few bytes.
    cores = []
    for va, chunk in code:
        for match in re.finditer(re.escape(XXH32_MINUS_PRIME2), chunk):
            window = chunk[max(0, match.start() - 64):match.start() + 64]
            if XXH32_PRIME1 in window:
                cores.append(va + match.start())
    if not cores:
        raise UnpackError("No XXH32 round loop found; this client build is not supported")

    # 2. The magic is both compared once (header check) and pushed as the hash seed.
    compared = {}
    for va, chunk in code:
        for match in CMP_IMM32.finditer(chunk):
            compared.setdefault(struct.unpack("<I", match.group(1))[0], []).append(va + match.start())
    pushed = {}
    for va, chunk in code:
        for match in PUSH_IMM32.finditer(chunk):
            value = struct.unpack("<I", match.group(1))[0]
            if value in compared:
                pushed.setdefault(value, []).append(va + match.start())
    seeds = []
    for value, sites in pushed.items():
        if len(sites) < 2 or len(compared[value]) != 1:
            continue
        # Every seed push must call the XXH32 routine it precedes.
        for site in sites:
            target = None
            for va, chunk in code:
                if va <= site < va + len(chunk):
                    local = site - va
                    for call in CALL_REL32.finditer(chunk[local:local + 24]):
                        target = site + call.start() + 5 + struct.unpack("<i", call.group(1))[0]
                        break
            if target is None or not any(0 <= core - target <= 0x200 for core in cores):
                break
        else:
            seeds.append(value)
    if len(seeds) != 1:
        raise UnpackError(f"Expected one archive magic/hash seed, found {len(seeds)}. "
                          "This client build is not supported; no constant was guessed.")
    magic = seeds[0]
    compare_va = compared[magic][0]
    seed_vas = sorted(pushed[magic])

    # 3. Pack-open routine: 64-bit header copy right after the magic comparison.
    window, window_base = None, 0
    for va, chunk in code:
        local = compare_va - va
        if 0 <= local < len(chunk):
            start = max(0, local - 0x200)
            window, window_base = chunk[start:local + 0x200], va + start
            break
    if window is None:
        raise UnpackError("The magic comparison is not inside an executable section")

    # The header copy is an alternating load/store chain right after the magic test.
    loads, stores = [], []
    previous = {True: None, False: None}
    base = None
    for match in re.finditer(rb"\x0f[\x10\x11]", window):
        if window_base + match.start() < compare_va:
            continue
        decoded = _modrm_displacement(window, match.start())
        if not decoded or decoded[1] not in (3, 5, 6, 7):
            break
        is_load, register, disp, _ = decoded
        if base is None:
            base = register
        if (register != base or is_load != (len(loads) == len(stores))
                or (previous[is_load] is not None and disp != previous[is_load] + AES_BLOCK)):
            break
        (loads if is_load else stores).append(disp)
        previous[is_load] = disp
    if not loads or len(loads) != len(stores):
        raise UnpackError("Could not read the header copy loop; this client build is not supported")
    blob_struct, blob_load = min(stores), min(loads)
    blob_size = max(loads) + AES_BLOCK - blob_load
    if blob_size <= 0 or blob_size != max(stores) + AES_BLOCK - blob_struct:
        raise UnpackError("The header copy loop is not a contiguous key blob")

    reads = []
    for match in HEADER_READ_CHAIN.finditer(window):
        size, modrm, disp, pushed = match.group(1)[0], match.group(2)[0], match.group(3)[0], match.group(4)[0] - 0x50
        if modrm >> 6 != 1 or modrm & 7 == 4 or (modrm >> 3) & 7 != pushed:
            continue
        reads.append((size, disp, window_base + match.start()))
    usable = [(size, disp, va) for size, disp, va in reads
              if size - (blob_load - disp) == blob_size and 0 < blob_load - disp < size]
    if len(usable) != 1:
        raise UnpackError(f"Expected one header read matching the key blob, found {len(usable)}")
    header_size, buffer_offset, header_read_va = usable[0]
    blob_offset = blob_load - buffer_offset

    # 4. Cipher arguments: key pointer, key length, IV pointer.
    chains = []
    for va, chunk in code:
        for match in KEY_ARGUMENT_CHAIN.finditer(chunk):
            chains.append((match.group(1)[0], match.group(2)[0], match.group(3)[0], va + match.start()))
    if not chains:
        raise UnpackError("No cipher key/IV argument chain found; this client build is not supported")
    if len({(a, b, c) for a, b, c, _ in chains}) != 1:
        raise UnpackError(f"Found {len(chains)} conflicting cipher argument chains; refusing to guess")
    iv_struct, key_length, key_struct, chain_va = chains[0]
    if key_length not in AES_KEY_LENGTHS:
        raise UnpackError(f"Unsupported cipher key length {key_length}; only AES-128/192/256 are handled")
    if iv_struct - key_struct < key_length or blob_offset + iv_struct - blob_struct + AES_BLOCK > header_size:
        raise UnpackError("The derived IV position does not fit the archive header")
    key_offset = blob_offset + key_struct - blob_struct
    iv_offset = blob_offset + iv_struct - blob_struct

    # 5. Supporting evidence: AES tables, CRC32 table, LZ4 loop, name normalization.
    sbox_offset = _first(AES_SBOX, data)
    if sbox_offset is None:
        raise UnpackError("No AES S-box in the client; the derived cipher cannot be AES")
    sbox_va = pe.offset_to_va(sbox_offset)
    sbox_refs = sum(chunk.count(struct.pack("<I", sbox_va)) for _, chunk in code)
    if not sbox_refs:
        raise UnpackError("The AES S-box is never referenced by executable code")
    crc_offset = _first(CRC32_TABLE, data)
    lz4_offset = _first(LZ4_TOKEN_LOOP, data)
    norm_offset = _first(NAME_BACKSLASH_TEST, data)
    if norm_offset is not None and NAME_BACKSLASH_FIX not in data[norm_offset:norm_offset + 32]:
        norm_offset = None
    mode_offsets = {name.rstrip(b"\0").decode(): _first(name, data) for name in MODE_NAMES}

    layout = Layout(
        magic=magic,
        header_size=header_size,
        blob_offset=blob_offset,
        blob_size=blob_size,
        key_offset=key_offset,
        key_length=key_length,
        iv_offset=iv_offset,
        iv_length=AES_BLOCK,
        reserved_offset=iv_offset + AES_BLOCK,
        reserved_length=header_size - (iv_offset + AES_BLOCK),
    )
    landmarks = {
        "xxh32_routine_va": [f"0x{core:x}" for core in sorted(cores)[:4]],
        "magic_compare_va": f"0x{compare_va:x}",
        "hash_seed_push_va": [f"0x{site:x}" for site in seed_vas],
        "header_read_va": f"0x{header_read_va:x}",
        "cipher_argument_chain_va": f"0x{chain_va:x}",
        "aes_sbox_va": f"0x{sbox_va:x}" if sbox_va else None,
        "aes_sbox_code_references": sbox_refs,
        "crc32_table_va": f"0x{pe.offset_to_va(crc_offset):x}" if crc_offset is not None else None,
        "lz4_block_decoder_va": f"0x{pe.offset_to_va(lz4_offset):x}" if lz4_offset is not None else None,
        "name_normalize_va": f"0x{pe.offset_to_va(norm_offset):x}" if norm_offset is not None else None,
        "cipher_mode_names": {name: (f"0x{pe.offset_to_va(off):x}" if off is not None and pe.offset_to_va(off) else None)
                              for name, off in mode_offsets.items()},
        "mask_xor_instructions": sum(1 for m in MASK_XOR_LOOP.finditer(window) if m.group()[1] & 7 != 4),
    }
    return ClientAnalysis(layout, landmarks, hashlib.sha256(data).hexdigest())


def read_key_material(archive: Path, layout: Layout,
                      key_mask: bytes = b"", iv_mask: bytes = b"") -> dict:
    """Read the archive's own key blob and apply the client's optional XOR masks."""
    with archive.open("rb") as stream:
        header = stream.read(layout.header_size)
    if len(header) < layout.header_size:
        raise UnpackError(f"Archive is shorter than its {layout.header_size}-byte header")
    if struct.unpack_from("<I", header, 0)[0] != layout.magic:
        raise UnpackError(f"Not a History pack: expected magic 0x{layout.magic:08x} at offset 0")
    blob = header[layout.blob_offset:layout.blob_offset + layout.blob_size]
    key = header[layout.key_offset:layout.key_offset + layout.key_length]
    iv = header[layout.iv_offset:layout.iv_offset + layout.iv_length]
    reserved = header[layout.reserved_offset:layout.reserved_offset + layout.reserved_length]

    def masked(value: bytes, mask: bytes, option: str) -> bytes:
        if not mask:
            return value
        if len(mask) != len(value):
            raise UnpackError(f"{option} must be exactly {len(value)} bytes ({len(value) * 2} hex digits)")
        return bytes(a ^ b for a, b in zip(value, mask))

    key = masked(key, key_mask, "--key-mask")
    iv = masked(iv, iv_mask, "--iv-mask")
    return {"key_hex": key.hex(), "iv_hex": iv.hex(), "reserved_hex": reserved.hex(),
            "blob_hex": blob.hex(), "key_masked": bool(key_mask), "iv_masked": bool(iv_mask),
            "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}


def read_index(path: Path, layout: Layout, max_file_size: int = DEFAULT_FILE_LIMIT,
               max_total_size: int = DEFAULT_TOTAL_LIMIT) -> list[Entry]:
    """Walk the interleaved entry headers and payloads; reject gaps and truncation."""
    size = path.stat().st_size
    if size < layout.header_size:
        raise UnpackError(f"Archive is shorter than its {layout.header_size}-byte header")
    entries: list[Entry] = []
    total = 0
    with path.open("rb") as stream:
        if struct.unpack("<I", stream.read(4))[0] != layout.magic:
            raise UnpackError(f"Not a History pack: expected magic 0x{layout.magic:08x} at offset 0")
        position = layout.header_size
        while position < size:
            stream.seek(position)
            data = stream.read(ENTRY_HEADER.size)
            if len(data) != ENTRY_HEADER.size:
                raise UnpackError(f"Truncated entry header at 0x{position:x}")
            entry = Entry(len(entries), position, *ENTRY_HEADER.unpack(data))
            if entry.data_offset < position + ENTRY_HEADER.size:
                raise UnpackError(f"Invalid payload offset at entry {entry.index}")
            if entry.data_offset + entry.stored_size > size:
                raise UnpackError(f"Truncated payload at entry {entry.index}")
            if not entry.stored_size and entry.original_size:
                raise UnpackError(f"Empty payload for nonempty entry {entry.index}")
            total += entry.original_size
            if max(entry.original_size, entry.stored_size) > max_file_size or total > max_total_size:
                raise UnpackError(f"Size safety limit exceeded at entry {entry.index}")
            entries.append(entry)
            if len(entries) > 1_000_000:
                raise UnpackError("Too many entries")
            position = entry.data_offset + entry.stored_size
    return entries


def decrypt_payload(data: bytes, key: bytes, iv: bytes) -> bytes:
    """AES-CFB with full-block feedback; the client restarts the IV for every entry."""
    _, _, aes = dependencies()
    return aes.new(key, aes.MODE_CFB, iv, segment_size=128).decrypt(data)


def decode_entry(stream, entry: Entry, key: bytes, iv: bytes, magic: int) -> bytes:
    lz4, xxhash, _ = dependencies()
    stream.seek(entry.data_offset)
    encrypted = stream.read(entry.stored_size)
    if len(encrypted) != entry.stored_size:
        raise UnpackError(f"Truncated payload at entry {entry.index}")
    packed = decrypt_payload(encrypted, key, iv)
    if not entry.compressed:
        payload = packed
    else:
        try:
            payload = lz4.decompress(packed, uncompressed_size=entry.original_size)
        except (ValueError, lz4.LZ4BlockError) as exc:
            raise UnpackError(f"LZ4 failure at entry {entry.index}: wrong key or damaged archive") from exc
    if len(payload) != entry.original_size:
        raise UnpackError(f"Size mismatch at entry {entry.index}")
    if xxhash.xxh32(payload, seed=magic).intdigest() != entry.checksum:
        raise UnpackError(f"XXH32 mismatch at entry {entry.index}; wrong key or damaged archive")
    return payload


def normalize_name(name: str) -> str:
    """Match the client: ASCII tolower, then backslashes become forward slashes."""
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


# Filenames are hints only: a candidate is accepted ONLY when its CRC32 matches an
# index hash, and a hash with several candidates stays unnamed.
PATH_PATTERN = re.compile(
    rb"[A-Za-z0-9_./:\\ -]{1,240}\.(?:pyc|pyo|py|md|rst|txt|json|xml|cfg|ini|csv|msm|msj|msa|mse|"
    rb"dds|tga|png|jpg|jpeg|bmp|psd|gr2|wav|mp3|ogg|avi|ttf|otf|d2|bin|dat|dll|exe)\b",
    re.IGNORECASE,
)
IMPORT_PATTERN = re.compile(
    rb"(?m)^[ \t]*(?:from|import)[ \t]+([A-Za-z_][A-Za-z0-9_.]*(?:[ \t]*,[ \t]*[A-Za-z_][A-Za-z0-9_.]*)*)")
DIRECTORY_PATTERN = re.compile(rb'''["']([A-Za-z0-9_.]{1,40}/)["']''')
CLIENT_ASCII_TOKEN = re.compile(rb"[!-~]{3,60}")
CLIENT_WIDE_TOKEN = re.compile(rb"(?:[\x21-\x7e]\x00){3,60}")
USABLE_TOKEN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_./\\-]{0,59}$")
PATH_TOKEN = re.compile(r"^[a-z0-9_.\-]+(?:/[a-z0-9_.\-]+)+\.(?:pyc|pyo|py|md|txt)$")
MODULE_TOKEN = re.compile(r"^[a-z_][a-z0-9_]{1,40}$")
MODULE_PATTERN = re.compile(rb"[A-Za-z_][A-Za-z0-9_]{1,63}(?![A-Za-z0-9_])")
SCRIPT_EXTENSIONS = (".py", ".pyc", ".pyo", ".md", ".txt")
SCRIPT_SUFFIXES = ("", ".py", ".pyc")
MAX_TOKENS = 400_000
MAX_MODULES = 200_000
MAX_PREFIXES = 8


class NameResolver:
    """Recover virtual filenames from CRC32 matches; never from decryption alone."""

    def __init__(self, hashes):
        self.hashes = set(hashes)
        self.matches: dict[int, set[str]] = {}
        self.tokens: set[str] = set()
        self.modules: set[str] = set()
        self.payload_modules: set[str] = set()
        self.prefix_weights: dict[str, int] = {}
        self.script_prefix_weights: dict[str, int] = {}
        self.extra_prefixes: set[str] = set()

    def match(self, name: str):
        """Accept an already normalized name only on an exact CRC32 hit."""
        if not name or len(name) > 240:
            return
        hashed = zlib.crc32(name.encode("utf-8")) & MASK
        if hashed not in self.hashes:
            return
        try:
            safe_relative_name(name)
        except UnpackError:
            return
        self.matches.setdefault(hashed, set()).add(name)

    def add(self, name: str):
        self.match(normalize_name(name.strip()))

    def add_prefix(self, prefix: str, weight: int = 1, script: bool = False):
        """Remember a directory seen in a real path; script dirs also expand modules."""
        prefix = normalize_name(prefix.strip())
        if prefix.endswith("/") and 2 <= len(prefix) <= 40 and re.match(r"^[a-z0-9_./-]+/$", prefix):
            table = self.script_prefix_weights if script else self.prefix_weights
            table[prefix] = table.get(prefix, 0) + weight

    def prefixes(self, script_only: bool = False) -> list[str]:
        weights = self.script_prefix_weights if script_only else self.prefix_weights
        ranked = sorted(weights, key=lambda p: (-weights[p], p))[:MAX_PREFIXES]
        return [""] + sorted(set(ranked) | self.extra_prefixes)

    def scan(self, data: bytes):
        """Harvest names from an already decoded payload; the payload is never run."""
        for match in PATH_PATTERN.finditer(data):
            text = match.group().decode("ascii", errors="ignore").strip()
            starts = {0} | {i + 1 for i, char in enumerate(text) if char in " /\\"}
            for start in starts:
                candidate = normalize_name(text[start:].strip())
                self.match(candidate)
                if "/" in candidate:
                    self.add_prefix(candidate[:candidate.rindex("/") + 1],
                                    script=candidate.endswith(SCRIPT_EXTENSIONS))
        prefixes = self.prefixes(script_only=True)
        for match in IMPORT_PATTERN.finditer(data):
            for part in match.group(1).decode("ascii", errors="ignore").split(","):
                module = normalize_name(part.strip()).replace(".", "/")
                for prefix in prefixes:
                    self.match(prefix + module + ".py")
                    self.match(prefix + module + ".pyc")
        for match in DIRECTORY_PATTERN.finditer(data):
            self.add_prefix(match.group(1).decode("ascii", errors="ignore"))
        if len(self.payload_modules) < MAX_MODULES:
            for match in MODULE_PATTERN.finditer(data):
                self.payload_modules.add(match.group().decode("ascii", errors="ignore").lower())
                if len(self.payload_modules) >= MAX_MODULES:
                    break

    def apply_modules(self):
        """Match identifiers seen inside payloads; run once, after every payload."""
        prefixes = self.prefixes(script_only=True)
        for module in sorted(self.payload_modules):
            if not MODULE_TOKEN.match(module):
                continue
            for prefix in prefixes:
                self.match(prefix + module + ".py")
                self.match(prefix + module + ".pyc")

    def harvest_client(self, data: bytes):
        """Collect filename-like tokens from the client's ASCII and UTF-16 strings."""
        counts: dict[str, int] = {}
        for pattern, encoding in ((CLIENT_ASCII_TOKEN, "ascii"), (CLIENT_WIDE_TOKEN, "utf-16le")):
            for match in pattern.finditer(data):
                token = match.group().decode(encoding, errors="ignore")
                if not USABLE_TOKEN.match(token):
                    continue
                token = normalize_name(token)
                if len(self.tokens) >= MAX_TOKENS and token not in self.tokens:
                    continue
                self.tokens.add(token)
                if "/" in token:
                    if PATH_TOKEN.match(token):
                        counts[token[:token.rindex("/") + 1]] = counts.get(token[:token.rindex("/") + 1], 0) + 1
                    self.match(token)
                elif MODULE_TOKEN.match(token):
                    self.modules.add(token)
        for prefix, weight in counts.items():
            self.add_prefix(prefix, weight, script=True)

    def apply_tokens(self):
        """Match client tokens; repeated after payload scanning reveals directories."""
        for token in sorted(self.tokens):
            for suffix in SCRIPT_SUFFIXES:
                self.match(token + suffix)
        prefixes = [prefix for prefix in self.prefixes() if prefix]
        if prefixes:
            for prefix in prefixes:
                for module in sorted(self.modules):
                    self.match(prefix + module + ".py")
                    self.match(prefix + module + ".pyc")

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


def process_archive(archive: Path, entries: list[Entry], layout: Layout, keys: dict,
                    resolver: NameResolver, output: Path | None) -> dict:
    """Verify every record; publish a fresh output directory only after success."""
    key, iv = bytes.fromhex(keys["key_hex"]), bytes.fromhex(keys["iv_hex"])
    summary = {"archive": str(archive), "files": len(entries),
               "original_bytes": sum(e.original_size for e in entries),
               "archive_sha256": keys["archive_sha256"]}
    if output is None:
        with archive.open("rb") as stream:
            for entry in entries:
                decode_entry(stream, entry, key, iv, layout.magic)
                progress(entry.index + 1, len(entries))
        return {**summary, "verified": len(entries)}
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise UnpackError(f"Output already exists (never overwritten): {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".history-unpack-", dir=output.parent) as temp:
        stage = Path(temp)
        spool = stage / "spool"
        spool.mkdir()
        result = stage / "result"
        result.mkdir()
        digests = []
        with archive.open("rb") as stream:
            for entry in entries:
                data = decode_entry(stream, entry, key, iv, layout.magic)
                digests.append(hashlib.sha256(data).hexdigest())
                (spool / str(entry.index)).write_bytes(data)
                resolver.scan(data)
                progress(entry.index + 1, len(entries))
        # Payloads may reveal directories (uiscript/) that name more client tokens.
        resolver.apply_tokens()
        resolver.apply_modules()
        records = []
        known = 0
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
                            "compressed": entry.compressed, "name": name,
                            "candidates": sorted(resolver.matches.get(entry.name_hash, [])),
                            "output": relative.as_posix(), "sha256": digest})
        summary.update(verified=len(entries), named=known, unknown=len(entries) - known)
        manifest = {**summary, "format": "History/AES-256-CFB/LZ4/XXH32",
                    "layout": asdict(layout), "entries": records}
        (result / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                              encoding="utf-8")
        if output.exists() or output.is_symlink():
            raise UnpackError("Output appeared during extraction; refusing to overwrite it")
        result.rename(output)
    return {**summary, "output": str(output)}


def validate_keys(archive: Path, entries: list[Entry], layout: Layout, keys: dict, count: int = 3) -> list[dict]:
    """Prove the derived key by decoding the first records and checking XXH32."""
    key, iv = bytes.fromhex(keys["key_hex"]), bytes.fromhex(keys["iv_hex"])
    results = []
    with archive.open("rb") as stream:
        for entry in entries[:count]:
            payload = decode_entry(stream, entry, key, iv, layout.magic)
            results.append({"index": entry.index, "name_hash": f"{entry.name_hash:08x}",
                            "original_size": entry.original_size,
                            "xxh32": f"{entry.checksum:08x}", "verified": True,
                            "preview": payload[:16].hex()})
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("key", "list", "verify", "extract"):
        help_text = {
            "key": "Derive the cipher geometry from the client and read the pack's key",
            "list": "List entry headers without decrypting payloads",
            "verify": "Decrypt and validate every file without saving it",
            "extract": "Decrypt, validate, recover filenames, and write the output tree",
        }[command]
        sub = commands.add_parser(command, help=help_text)
        sub.add_argument("archive", nargs="?", type=Path, default=DEFAULT_ARCHIVE)
        sub.add_argument("--client", type=Path, default=DEFAULT_CLIENT)
        sub.add_argument("--key-mask", default="", metavar="HEX",
                         help="Optional XOR mask for the header key, as 64 hex digits")
        sub.add_argument("--iv-mask", default="", metavar="HEX",
                         help="Optional XOR mask for the header IV, as 32 hex digits")
        sub.add_argument("--max-file-size", type=int, default=DEFAULT_FILE_LIMIT, metavar="BYTES")
        sub.add_argument("--max-total-size", type=int, default=DEFAULT_TOTAL_LIMIT, metavar="BYTES")
        if command != "key":
            sub.add_argument("--names", type=Path, action="append", default=[],
                             help="UTF-8 filename list, one per line; repeatable")
            sub.add_argument("--prefix", action="append", default=[],
                             help="Directory prefix tried against client tokens; repeatable")
        if command == "extract":
            sub.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT,
                             help="New directory; an existing output is never overwritten")
    return parser


def _mask(value: str) -> bytes:
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise UnpackError(f"Masks must be hexadecimal: {exc}") from exc


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.max_file_size <= 0 or args.max_total_size <= 0:
            raise UnpackError("Size limits must be positive")
        client = args.client.read_bytes()
        analysis = analyze_client(client)
        layout = analysis.layout
        keys = read_key_material(args.archive, layout, _mask(args.key_mask), _mask(args.iv_mask))
        if args.command == "key":
            entries = read_index(args.archive, layout, args.max_file_size, args.max_total_size)
            dependencies()
            print(json.dumps({**analysis.to_dict(), "archive": str(args.archive),
                              "entries": len(entries), **keys,
                              "validated": validate_keys(args.archive, entries, layout, keys)},
                             indent=2, ensure_ascii=False))
            return 0
        entries = read_index(args.archive, layout, args.max_file_size, args.max_total_size)
        resolver = NameResolver(e.name_hash for e in entries)
        resolver.harvest_client(client)
        for prefix in getattr(args, "prefix", []):
            resolver.extra_prefixes.add(normalize_name(prefix if prefix.endswith("/") else prefix + "/"))
        resolver.apply_tokens()
        for path in getattr(args, "names", []):
            resolver.load(path)
        if args.command == "list":
            print("INDEX\tNAME_HASH\tORIGINAL\tSTORED\tDATA_OFFSET\tNAME (unverified payload)")
            for entry in entries:
                print(f"{entry.index}\t{entry.name_hash:08x}\t{entry.original_size}\t"
                      f"{entry.stored_size}\t{entry.data_offset}\t"
                      f"{resolver.resolved(entry.name_hash) or '-'}")
            return 0
        dependencies()
        summary = process_archive(args.archive, entries, layout, keys, resolver,
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
