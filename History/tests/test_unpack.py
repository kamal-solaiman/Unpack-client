"""Unit tests use a synthetic client and synthetic packs; integration tests read originals only."""
import contextlib
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import unpack

lz4, xxhash, AES = unpack.dependencies()
MAGIC = 0x0BADF00D
KEY = bytes(range(32))
IV = bytes(range(0x40, 0x50))
RESERVED = bytes(range(0x60, 0x70))
TEXT_RAW, TEXT_SIZE, TEXT_RVA = 0x400, 0x400, 0x1000
DATA_RAW, DATA_SIZE, DATA_RVA = 0x800, 0x200, 0x2000
IMAGE_BASE = 0x400000


def encrypt(data: bytes, key: bytes = KEY, iv: bytes = IV) -> bytes:
    """Independent forward AES-256-CFB (full-block feedback) for fixture construction."""
    return AES.new(key, AES.MODE_CFB, iv, segment_size=128).encrypt(data)


def archive_bytes(items, key: bytes = KEY, iv: bytes = IV, magic: int = MAGIC) -> bytes:
    """Header with the key blob, then interleaved entry headers and payloads."""
    result = bytearray(struct.pack("<I", magic) + key + iv + RESERVED)
    assert len(result) == 0x44
    for name, payload, compress in items:
        packed = lz4.compress(payload, store_size=False) if compress else payload
        encrypted = encrypt(packed, key, iv)
        result.extend(struct.pack("<5I", len(payload),
                                  xxhash.xxh32(payload, seed=magic).intdigest(),
                                  len(result) + unpack.ENTRY_HEADER.size, len(encrypted),
                                  unpack.name_hash(name)))
        result.extend(encrypted)
    return bytes(result)


def synthetic_pe(magic: int = MAGIC) -> bytearray:
    """A 32-bit PE carrying every landmark analyze_client() derives the layout from."""
    text, data = bytearray(TEXT_SIZE), bytearray(DATA_SIZE)

    # XXH32 round loop: multiply by -PRIME2 with PRIME1 close by.
    text[0x00:0x06] = b"\x55\x8b\xec\x8b\x45\x08"
    text[0x10:0x16] = b"\x69\x0a" + unpack.XXH32_MINUS_PRIME2
    text[0x20:0x26] = b"\x69\xff" + unpack.XXH32_PRIME1
    core_va = IMAGE_BASE + TEXT_RVA + 0x12

    # Pack open: read the 0x44-byte header from [esi+0x60], test the magic, copy the blob.
    text[0x100:0x105] = b"\x6a\x44\x8d\x7e\x60"          # push 0x44; lea edi,[esi+0x60]
    text[0x105:0x106] = b"\x57"                            # push edi
    text[0x110:0x116] = b"\x81\x3f" + struct.pack("<I", magic)
    copies = [(b"\x0f\x10\x46\x64", b"\x0f\x11\x46\x20"),   # [esi+0x64] -> [esi+0x20]
              (b"\x0f\x10\x46\x74", b"\x0f\x11\x46\x30"),
              (b"\x0f\x10\x86" + struct.pack("<i", 0x84), b"\x0f\x11\x46\x40"),
              (b"\x0f\x10\x86" + struct.pack("<i", 0x94), b"\x0f\x11\x46\x50")]
    offset = 0x120
    for load, store in copies:
        text[offset:offset + len(load)] = load
        offset += len(load)
        text[offset:offset + len(store)] = store
        offset += len(store)
    text[0x180:0x186] = b"\x31\x46\x20\x31\x46\x24"      # the optional mask XOR loop

    # Two hash-seed pushes, each immediately calling the XXH32 routine.
    for site in (0x200, 0x220):
        text[site] = 0x68
        struct.pack_into("<I", text, site + 1, magic)
        text[site + 5] = 0xE8
        struct.pack_into("<i", text, site + 6, (core_va - 0x10) - (IMAGE_BASE + TEXT_RVA + site + 10))

    # Cipher construction: push iv; push key length; push key.
    text[0x240:0x243] = b"\x8d\x46\x40"                  # lea eax,[esi+0x40]
    text[0x243:0x247] = b"\xc6\x45\xfc\x04"
    text[0x247:0x24E] = b"\x50\x6a\x20\x8d\x46\x20\x50"

    sbox_va = IMAGE_BASE + DATA_RVA + 0x20
    text[0x260] = 0x68                                   # push sbox_va: a code reference
    struct.pack_into("<I", text, 0x261, sbox_va)
    text[0x280:0x280 + len(unpack.LZ4_TOKEN_LOOP)] = unpack.LZ4_TOKEN_LOOP
    text[0x2A0:0x2A0 + len(unpack.NAME_BACKSLASH_TEST)] = unpack.NAME_BACKSLASH_TEST
    text[0x2B0:0x2B0 + len(unpack.NAME_BACKSLASH_FIX)] = unpack.NAME_BACKSLASH_FIX

    data[0x20:0x20 + len(unpack.AES_SBOX)] = unpack.AES_SBOX
    data[0x40:0x40 + len(unpack.CRC32_TABLE)] = unpack.CRC32_TABLE
    data[0x60:0x71] = b"CFB\0AES\0Feedback\0"

    image = bytearray(DATA_RAW + DATA_SIZE)
    image[0:2] = b"MZ"
    struct.pack_into("<I", image, 0x3C, 0x80)
    image[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HH", image, 0x84, 0x14C, 2)       # i386, two sections
    struct.pack_into("<H", image, 0x94, 0xE0)            # SizeOfOptionalHeader
    struct.pack_into("<H", image, 0x98, 0x10B)           # PE32
    struct.pack_into("<I", image, 0xB4, IMAGE_BASE)
    for header, name, rva, raw, size, flags in (
            (0x178, b".text", TEXT_RVA, TEXT_RAW, TEXT_SIZE, 0x60000020),
            (0x1A0, b".data", DATA_RVA, DATA_RAW, DATA_SIZE, 0xC0000040)):
        struct.pack_into("<8s4I", image, header, name, size, rva, size, raw)
        struct.pack_into("<I", image, header + 36, flags)
    assert (len(text), len(data)) == (TEXT_SIZE, DATA_SIZE), "fixture slices must not resize"
    image[TEXT_RAW:TEXT_RAW + TEXT_SIZE] = text
    image[DATA_RAW:DATA_RAW + DATA_SIZE] = data
    assert len(image) == DATA_RAW + DATA_SIZE
    return image


class AnalysisTests(unittest.TestCase):
    def test_derives_geometry_from_code(self):
        analysis = unpack.analyze_client(bytes(synthetic_pe()))
        layout = analysis.layout
        self.assertEqual(layout.magic, MAGIC)
        self.assertEqual((layout.header_size, layout.blob_offset, layout.blob_size), (0x44, 4, 64))
        self.assertEqual((layout.key_offset, layout.key_length), (4, 32))
        self.assertEqual((layout.iv_offset, layout.iv_length), (36, 16))
        self.assertEqual((layout.reserved_offset, layout.reserved_length), (52, 16))
        self.assertEqual(analysis.landmarks["cipher_mode_names"]["CFB"], "0x402060")
        self.assertEqual(analysis.landmarks["aes_sbox_va"], "0x402020")
        self.assertEqual(analysis.landmarks["crc32_table_va"], "0x402040")
        self.assertEqual(analysis.landmarks["aes_sbox_code_references"], 1)
        self.assertGreaterEqual(analysis.landmarks["mask_xor_instructions"], 2)

    def test_magic_is_derived_not_assumed(self):
        self.assertEqual(unpack.analyze_client(bytes(synthetic_pe(0x12345678))).layout.magic, 0x12345678)

    def test_missing_aes_sbox_rejected(self):
        image = synthetic_pe()
        image[DATA_RAW + 0x20:DATA_RAW + 0x20 + len(unpack.AES_SBOX)] = b"\0" * len(unpack.AES_SBOX)
        with self.assertRaisesRegex(unpack.UnpackError, "S-box"):
            unpack.analyze_client(bytes(image))

    def test_unreferenced_sbox_rejected(self):
        image = synthetic_pe()
        image[TEXT_RAW + 0x260:TEXT_RAW + 0x265] = b"\x90" * 5
        with self.assertRaisesRegex(unpack.UnpackError, "never referenced"):
            unpack.analyze_client(bytes(image))

    def test_conflicting_cipher_chains_rejected(self):
        image = synthetic_pe()
        second = TEXT_RAW + 0x340
        image[second:second + 3] = b"\x8d\x46\x48"
        image[second + 3:second + 7] = b"\x90" * 4
        image[second + 7:second + 14] = b"\x50\x6a\x20\x8d\x46\x20\x50"
        with self.assertRaisesRegex(unpack.UnpackError, "conflicting"):
            unpack.analyze_client(bytes(image))

    def test_iv_inside_the_key_rejected(self):
        image = synthetic_pe()
        image[TEXT_RAW + 0x242] = 0x30  # the IV would start inside the 32-byte key
        with self.assertRaisesRegex(unpack.UnpackError, "IV position"):
            unpack.analyze_client(bytes(image))

    def test_unsupported_key_length_rejected(self):
        image = synthetic_pe()
        image[TEXT_RAW + 0x249] = 0x11  # push 17: not an AES key length
        with self.assertRaisesRegex(unpack.UnpackError, "key length"):
            unpack.analyze_client(bytes(image))

    def test_missing_seed_pushes_rejected(self):
        image = synthetic_pe()
        for site in (0x200, 0x220):
            image[TEXT_RAW + site] = 0x90
        with self.assertRaisesRegex(unpack.UnpackError, "magic"):
            unpack.analyze_client(bytes(image))

    def test_broken_header_copy_rejected(self):
        image = synthetic_pe()
        image[TEXT_RAW + 0x122] = 0x45  # load from [ebp+0x64] instead of [esi+0x64]
        with self.assertRaisesRegex(unpack.UnpackError, "header copy loop"):
            unpack.analyze_client(bytes(image))

    def test_header_read_mismatch_rejected(self):
        image = synthetic_pe()
        image[TEXT_RAW + 0x101] = 0x40  # reads 0x40 bytes but copies a 0x40-byte blob at +4
        with self.assertRaisesRegex(unpack.UnpackError, "header read"):
            unpack.analyze_client(bytes(image))

    def test_not_a_pe(self):
        for data in (b"", b"MZ", bytes(synthetic_pe())[:0x300], b"\0" * 0xA00):
            with self.assertRaises(unpack.UnpackError):
                unpack.analyze_client(data)


class CryptoTests(unittest.TestCase):
    def test_round_trip(self):
        payload = bytes(range(256)) * 3 + b"tail"
        self.assertEqual(unpack.decrypt_payload(encrypt(payload), KEY, IV), payload)

    def test_iv_restarts_per_entry(self):
        payload = b"A" * 64
        self.assertEqual(encrypt(payload), encrypt(payload))
        self.assertNotEqual(encrypt(payload), encrypt(payload, iv=bytes(16)))

    def test_empty_payload(self):
        self.assertEqual(unpack.decrypt_payload(b"", KEY, IV), b"")


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "workplace.d2"
        self.items = [("ui/a.py", b"import b\n" * 200, True),
                      ("b.pyc", b"\x03\xf3\r\n" + bytes(range(200)), True),
                      ("empty.txt", b"", False)]
        self.archive.write_bytes(archive_bytes(self.items))
        self.layout = unpack.analyze_client(bytes(synthetic_pe())).layout
        self.keys = {"key_hex": KEY.hex(), "iv_hex": IV.hex(), "archive_sha256": "synthetic"}

    def decode(self, entry, key=KEY, iv=IV):
        with self.archive.open("rb") as stream:
            return unpack.decode_entry(stream, entry, key, iv, self.layout.magic)

    def test_mixed_archive(self):
        entries = unpack.read_index(self.archive, self.layout)
        self.assertEqual([self.decode(e) for e in entries], [payload for _, payload, _ in self.items])
        self.assertEqual([e.compressed for e in entries], [True, True, False])
        self.assertEqual([e.header_offset for e in entries][0], 0x44)

    def test_bad_magic(self):
        self.archive.write_bytes(struct.pack("<I", MAGIC ^ 1) + KEY + IV + RESERVED)
        with self.assertRaisesRegex(unpack.UnpackError, "magic"):
            unpack.read_index(self.archive, self.layout)

    def test_short_header(self):
        self.archive.write_bytes(struct.pack("<I", MAGIC) + KEY)
        with self.assertRaisesRegex(unpack.UnpackError, "shorter"):
            unpack.read_index(self.archive, self.layout)

    def test_truncated_entry_header(self):
        self.archive.write_bytes(archive_bytes(self.items) + b"x" * 5)
        with self.assertRaisesRegex(unpack.UnpackError, "Truncated entry header"):
            unpack.read_index(self.archive, self.layout)

    def test_truncated_payload(self):
        self.archive.write_bytes(archive_bytes(self.items[:1])[:-1])
        with self.assertRaisesRegex(unpack.UnpackError, "Truncated payload"):
            unpack.read_index(self.archive, self.layout)

    def test_payload_before_header(self):
        blob = bytearray(archive_bytes(self.items))
        struct.pack_into("<I", blob, 0x44 + 8, 0x44)
        self.archive.write_bytes(blob)
        with self.assertRaisesRegex(unpack.UnpackError, "Invalid payload offset"):
            unpack.read_index(self.archive, self.layout)

    def test_empty_payload_for_nonempty_entry(self):
        blob = bytearray(archive_bytes(self.items))
        struct.pack_into("<I", blob, 0x44 + 12, 0)
        self.archive.write_bytes(blob)
        with self.assertRaisesRegex(unpack.UnpackError, "Empty payload"):
            unpack.read_index(self.archive, self.layout)

    def test_limits(self):
        for kwargs in ({"max_file_size": 1}, {"max_total_size": 1}):
            with self.assertRaisesRegex(unpack.UnpackError, "limit"):
                unpack.read_index(self.archive, self.layout, **kwargs)

    def test_checksum_corruption(self):
        blob = bytearray(archive_bytes(self.items))
        blob[0x48] ^= 1  # the stored XXH32 of the first entry
        self.archive.write_bytes(blob)
        with self.assertRaisesRegex(unpack.UnpackError, "XXH32"):
            self.decode(unpack.read_index(self.archive, self.layout)[0])

    def test_payload_corruption(self):
        blob = bytearray(archive_bytes(self.items))
        blob[0x58] ^= 1  # the first encrypted byte of the first payload
        self.archive.write_bytes(blob)
        with self.assertRaisesRegex(unpack.UnpackError, "XXH32|LZ4"):
            self.decode(unpack.read_index(self.archive, self.layout)[0])

    def test_wrong_key(self):
        entry = unpack.read_index(self.archive, self.layout)[0]
        with self.assertRaises(unpack.UnpackError):
            self.decode(entry, key=bytes(32))

    def test_key_material_and_masks(self):
        keys = unpack.read_key_material(self.archive, self.layout)
        self.assertEqual(keys["key_hex"], KEY.hex())
        self.assertEqual(keys["iv_hex"], IV.hex())
        self.assertEqual(keys["reserved_hex"], RESERVED.hex())
        self.assertFalse(keys["key_masked"] or keys["iv_masked"])
        masked = unpack.read_key_material(self.archive, self.layout, bytes(32), b"\xff" * 16)
        self.assertEqual(masked["key_hex"], KEY.hex())
        self.assertEqual(masked["iv_hex"], bytes(b ^ 0xFF for b in IV).hex())
        self.assertTrue(masked["iv_masked"])
        with self.assertRaisesRegex(unpack.UnpackError, "exactly"):
            unpack.read_key_material(self.archive, self.layout, b"\0" * 8)

    def test_extraction_and_manifest(self):
        entries = unpack.read_index(self.archive, self.layout)
        resolver = unpack.NameResolver(e.name_hash for e in entries)
        resolver.add("ui/a.py")
        out = self.root / "out"
        with contextlib.redirect_stderr(io.StringIO()):
            summary = unpack.process_archive(self.archive, entries, self.layout, self.keys, resolver, out)
        self.assertEqual(summary["verified"], 3)
        self.assertEqual(summary["named"], 2)  # b.pyc is recovered from the import in ui/a.py
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertEqual(manifest["format"], "History/AES-256-CFB/LZ4/XXH32")
        self.assertEqual(manifest["layout"]["key_length"], 32)
        self.assertEqual((out / "files/ui/a.py").read_bytes(), self.items[0][1])
        self.assertEqual((out / "files/b.pyc").read_bytes(), self.items[1][1])
        self.assertEqual((out / manifest["entries"][2]["output"]).read_bytes(), b"")
        self.assertTrue(manifest["entries"][2]["output"].startswith("unknown/"))
        self.assertFalse(list(self.root.glob(".history-unpack-*")))

    def test_no_overwrite(self):
        out = self.root / "out"
        out.mkdir()
        (out / "sentinel").write_text("keep")
        with self.assertRaisesRegex(unpack.UnpackError, "already exists"):
            unpack.process_archive(self.archive, unpack.read_index(self.archive, self.layout),
                                   self.layout, self.keys, unpack.NameResolver([]), out)
        self.assertEqual((out / "sentinel").read_text(), "keep")

    def test_symlink_output_rejected(self):
        out = self.root / "link"
        try:
            out.symlink_to(self.root / "nonexistent", target_is_directory=True)
        except OSError:
            self.skipTest("Symlinks unavailable")
        with self.assertRaisesRegex(unpack.UnpackError, "already exists"):
            unpack.process_archive(self.archive, unpack.read_index(self.archive, self.layout),
                                   self.layout, self.keys, unpack.NameResolver([]), out)

    def test_no_partial_output_on_failure(self):
        blob = bytearray(archive_bytes(self.items))
        entries = unpack.read_index(self.archive, self.layout)
        blob[entries[1].data_offset] ^= 1  # corrupt the second payload, after the first is staged
        blob[entries[1].header_offset + 8] = entries[1].data_offset
        self.archive.write_bytes(blob)
        out = self.root / "out"
        with self.assertRaises(unpack.UnpackError):
            unpack.process_archive(self.archive, unpack.read_index(self.archive, self.layout),
                                   self.layout, self.keys, unpack.NameResolver([]), out)
        self.assertFalse(out.exists())
        self.assertFalse(list(self.root.glob(".history-unpack-*")))

    def test_verify_writes_nothing(self):
        with contextlib.redirect_stderr(io.StringIO()):
            result = unpack.process_archive(self.archive, unpack.read_index(self.archive, self.layout),
                                            self.layout, self.keys, unpack.NameResolver([]), None)
        self.assertEqual(result["verified"], 3)
        self.assertEqual(list(self.root.iterdir()), [self.archive])


class NameTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(unpack.normalize_name("UIScript\\CamModule.PY"), "uiscript/cammodule.py")
        self.assertEqual(unpack.name_hash("ui.py"), 0x850BFBAF)
        self.assertEqual(unpack.name_hash("UI\\A.PY"), unpack.name_hash("ui/a.py"))

    def test_traversal_and_windows_hazards(self):
        for name in ("../a", "/etc/passwd", "a/../../b", "\\\\host\\file", "a//b", "c:foo",
                     "a\x00b", "a/CON.txt", "a/x.", "x:stream", "a/./b", ""):
            with self.subTest(name=name), self.assertRaises(unpack.UnpackError):
                unpack.safe_relative_name(name)
        self.assertEqual(unpack.safe_relative_name("D:\\ymir work\\a.tga").as_posix(), "_drives/d/ymir work/a.tga")

    def test_ambiguous_hash_stays_unnamed(self):
        resolver = unpack.NameResolver([123])
        resolver.matches[123] = {"a.py", "b.py"}
        self.assertIsNone(resolver.resolved(123))

    def test_unsafe_match_ignored(self):
        resolver = unpack.NameResolver([unpack.name_hash("../bad.py")])
        resolver.add("../bad.py")
        self.assertFalse(resolver.matches)

    def test_client_tokens_and_script_prefixes(self):
        names = ["uiscript/aebelt.py", "plainmodule.py", "unused/name.txt"]
        resolver = unpack.NameResolver(map(unpack.name_hash, names))
        client = (b"uiscript\\aebelt.py\0" + b"\0" * 24 + b"plainmodule\0" + b"\0" * 24
                  + "uiscript/other.py".encode("utf-16le") + b"\0\0")
        resolver.harvest_client(client)
        resolver.apply_tokens()
        self.assertEqual(resolver.prefixes(script_only=True), ["", "uiscript/"])
        self.assertEqual(resolver.resolved(unpack.name_hash("uiscript/aebelt.py")), "uiscript/aebelt.py")
        self.assertEqual(resolver.resolved(unpack.name_hash("plainmodule.py")), "plainmodule.py")
        self.assertNotIn(unpack.name_hash("unused/name.txt"), resolver.matches)

    def test_payload_modules_named_after_scan(self):
        target = "uiscript/test_affect.py"
        resolver = unpack.NameResolver([unpack.name_hash(target)])
        resolver.scan(b"# uiscript/x.py\nimport test_affect\nclass TestGame(ui.Window):\n    pass\n")
        resolver.apply_modules()
        self.assertEqual(resolver.resolved(unpack.name_hash(target)), target)

    def test_names_file(self):
        resolver = unpack.NameResolver([unpack.name_hash("a.py")])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "names.txt"
            path.write_text("# comment\n\na.py\n", encoding="utf-8")
            resolver.load(path)
        self.assertEqual(resolver.resolved(unpack.name_hash("a.py")), "a.py")


@unittest.skipUnless((unpack.HERE / "History2.exe").exists() and unpack.DEFAULT_ARCHIVE.exists(),
                     "Supplied History files not present")
class SuppliedFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analysis = unpack.analyze_client((unpack.HERE / "History2.exe").read_bytes())
        cls.layout = cls.analysis.layout
        cls.keys = unpack.read_key_material(unpack.DEFAULT_ARCHIVE, cls.layout)
        cls.entries = unpack.read_index(unpack.DEFAULT_ARCHIVE, cls.layout)

    def test_derived_layout(self):
        self.assertEqual(self.layout.magic, 0xF00FED5C)
        self.assertEqual((self.layout.header_size, self.layout.key_offset, self.layout.key_length), (0x44, 4, 32))
        self.assertEqual((self.layout.iv_offset, self.layout.iv_length), (36, 16))
        self.assertEqual((self.layout.reserved_offset, self.layout.reserved_length), (52, 16))
        self.assertEqual(self.analysis.landmarks["magic_compare_va"], "0x8e06c2")
        self.assertEqual(len(self.analysis.landmarks["hash_seed_push_va"]), 2)

    def test_index(self):
        self.assertEqual(len(self.entries), 813)
        self.assertEqual(sum(e.original_size for e in self.entries), 16929395)
        self.assertTrue(all(e.compressed for e in self.entries))
        self.assertEqual(self.entries[0].data_offset, self.entries[0].header_offset + 20)

    def test_first_file(self):
        with unpack.DEFAULT_ARCHIVE.open("rb") as stream:
            data = unpack.decode_entry(stream, self.entries[0], bytes.fromhex(self.keys["key_hex"]),
                                       bytes.fromhex(self.keys["iv_hex"]), self.layout.magic)
        self.assertEqual(len(data), 29428)
        self.assertTrue(data.startswith(b"#" * 16))

    def test_name_recovery_covers_the_archive(self):
        resolver = unpack.NameResolver(e.name_hash for e in self.entries)
        resolver.harvest_client((unpack.HERE / "History2.exe").read_bytes())
        resolver.apply_tokens()
        named = sum(1 for e in self.entries if resolver.resolved(e.name_hash))
        self.assertGreaterEqual(named, 800)

    @unittest.skipUnless(os.environ.get("HISTORY_FULL_TEST") == "1",
                         "Set HISTORY_FULL_TEST=1 to verify all 813 payloads")
    def test_all_files(self):
        key, iv = bytes.fromhex(self.keys["key_hex"]), bytes.fromhex(self.keys["iv_hex"])
        with unpack.DEFAULT_ARCHIVE.open("rb") as stream:
            for entry in self.entries:
                with self.subTest(entry=entry.index):
                    unpack.decode_entry(stream, entry, key, iv, self.layout.magic)


if __name__ == "__main__":
    unittest.main()
