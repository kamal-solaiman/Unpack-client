"""Unit tests use synthetic archives; integration tests read originals only."""
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

lz4, xxhash = unpack.dependencies()
KEY = bytes.fromhex("54d82039aa8d2722dc23e81c696b7430")


def encrypt(data, key=KEY):
    """Independent forward XTEA loop for fixture construction."""
    words = struct.unpack("<4I", key)
    data += b"\0" * (-len(data) % 8)
    result = bytearray()
    for a, b in struct.iter_unpack("<2I", data):
        total = 0
        for _ in range(4):
            a = (a + ((((b << 4) ^ (b >> 5)) + b) ^ (total + words[total & 3]))) & 0xFFFFFFFF
            total = (total + 0x9E3779B9) & 0xFFFFFFFF
            b = (b + ((((a << 4) ^ (a >> 5)) + a) ^ (total + words[(total >> 11) & 3]))) & 0xFFFFFFFF
        result.extend(struct.pack("<2I", a, b))
    return bytes(result)


def archive_bytes(items):
    result = bytearray(struct.pack("<I", unpack.MAGIC))
    for name, payload, compress in items:
        packed = lz4.compress(payload, store_size=False) if compress else payload
        encrypted = encrypt(packed)
        result.extend(struct.pack("<6I", len(payload), len(encrypted),
                                  xxhash.xxh32(payload, seed=unpack.MAGIC).intdigest(),
                                  len(result) + 24, len(packed), unpack.name_hash(name)))
        result.extend(encrypted)
    return result


def synthetic_pe():
    data = bytearray(0x600)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HH", data, 0x84, 0x8664, 2)
    struct.pack_into("<H", data, 0x94, 0xF0)
    struct.pack_into("<H", data, 0x98, 0x20B)
    struct.pack_into("<Q", data, 0xB0, 0x140000000)
    for off, name, rva, raw, flags in ((0x188, b".text", 0x1000, 0x200, 0x60000020),
                                       (0x1B0, b".data", 0x3000, 0x400, 0xC0000040)):
        struct.pack_into("<8s4I", data, off, name, 0x200, rva, 0x200, raw)
        struct.pack_into("<I", data, off + 36, flags)
    pattern = bytearray.fromhex("8b1e8bcbc1e9058bc3448b1d000000008b7e04488d7608448b15000000004c8b05000000008b1500000000c1e00481c272f36e3c")
    for end, target in ((16, 0x3020), (30, 0x302C), (37, 0x3024), (43, 0x3028)):
        struct.pack_into("<i", pattern, end - 4, target - (0x1000 + end))
    data[0x200:0x200 + len(pattern)] = pattern
    data[0x420:0x430] = KEY
    return data


class CryptoTests(unittest.TestCase):
    def test_known_client_vector(self):
        self.assertEqual(unpack.decrypt_xtea4(bytes.fromhex("178b82d729960259"), KEY), b"\xb7ScriptT")

    def test_round_trip_multiple_blocks(self):
        data = bytes(range(256))
        self.assertEqual(unpack.decrypt_xtea4(encrypt(data), KEY), data)

    def test_bad_key_or_alignment(self):
        for data, key in ((b"x", KEY), (b"12345678", b"bad")):
            with self.assertRaises(unpack.UnpackError):
                unpack.decrypt_xtea4(data, key)

    def test_empty_data(self):
        self.assertEqual(unpack.decrypt_xtea4(b"", KEY), b"")


class KeyTests(unittest.TestCase):
    def test_discover_relocated_key(self):
        result = unpack.discover_key(bytes(synthetic_pe()))
        self.assertEqual(result["key_hex"], KEY.hex())
        self.assertEqual(result["key_file_offset"], "0x420")
        self.assertEqual(result["key_rva"], "0x3020")

    def test_wrong_reference_relationship(self):
        data = synthetic_pe()
        data[0x200 + 26] ^= 1
        with self.assertRaises(unpack.UnpackError):
            unpack.discover_key(bytes(data))

    def test_truncated_pe(self):
        for data in (b"", b"MZ", bytes(synthetic_pe()[:0x500])):
            with self.assertRaises(unpack.UnpackError):
                unpack.discover_key(data)

    def test_unsupported_pe(self):
        data = synthetic_pe()
        data[0x200:0x240] = b"\0" * 64
        with self.assertRaisesRegex(unpack.UnpackError, "found 0"):
            unpack.discover_key(bytes(data))

    def test_ambiguous_routines_rejected(self):
        data = synthetic_pe()
        copied = bytearray(data[0x200:0x240])
        for end in (16, 30, 37, 43):
            displacement = struct.unpack_from("<i", copied, end - 4)[0]
            struct.pack_into("<i", copied, end - 4, displacement - 0x80)
        data[0x280:0x280 + len(copied)] = copied
        with self.assertRaisesRegex(unpack.UnpackError, "found 2"):
            unpack.discover_key(bytes(data))


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "root"
        self.items = [("a.py", b"import b\n" * 100, True), ("b.py", b"print('hello')\n", False),
                      ("empty.txt", b"", False)]
        self.archive.write_bytes(archive_bytes(self.items))
        self.info = {"key_hex": KEY.hex(), "client_sha256": "synthetic"}

    def test_mixed_archive(self):
        entries = unpack.read_index(self.archive)
        with self.archive.open("rb") as stream:
            self.assertEqual([unpack.decode_entry(stream, e, KEY) for e in entries],
                             [payload for _, payload, _ in self.items])

    def test_bad_magic(self):
        self.archive.write_bytes(b"EPKD")
        with self.assertRaisesRegex(unpack.UnpackError, "magic"):
            unpack.read_index(self.archive)

    def test_truncated_header(self):
        self.archive.write_bytes(struct.pack("<I", unpack.MAGIC) + b"x")
        with self.assertRaisesRegex(unpack.UnpackError, "header"):
            unpack.read_index(self.archive)

    def test_truncated_payload(self):
        self.archive.write_bytes(archive_bytes(self.items[:1])[:-1])
        with self.assertRaisesRegex(unpack.UnpackError, "Truncated payload"):
            unpack.read_index(self.archive)

    def test_invalid_offset(self):
        data = archive_bytes(self.items)
        struct.pack_into("<I", data, 16, 0xFFFFFFFF)
        self.archive.write_bytes(data)
        with self.assertRaisesRegex(unpack.UnpackError, "offset"):
            unpack.read_index(self.archive)

    def test_invalid_alignment(self):
        data = archive_bytes(self.items)
        struct.pack_into("<I", data, 8, 1)
        self.archive.write_bytes(data)
        with self.assertRaisesRegex(unpack.UnpackError, "block size"):
            unpack.read_index(self.archive)

    def test_limits(self):
        for kwargs in ({"max_file_size": 1}, {"max_total_size": 1}):
            with self.assertRaisesRegex(unpack.UnpackError, "limit"):
                unpack.read_index(self.archive, **kwargs)

    def test_checksum_corruption(self):
        data = archive_bytes(self.items)
        data[12] ^= 1
        self.archive.write_bytes(data)
        entries = unpack.read_index(self.archive)
        with self.archive.open("rb") as stream, self.assertRaisesRegex(unpack.UnpackError, "XXH32"):
            unpack.decode_entry(stream, entries[0], KEY)

    def test_wrong_key(self):
        entries = unpack.read_index(self.archive)
        with self.archive.open("rb") as stream, self.assertRaises(unpack.UnpackError):
            unpack.decode_entry(stream, entries[0], b"\0" * 16)

    def test_extraction_and_manifest(self):
        entries = unpack.read_index(self.archive)
        resolver = unpack.NameResolver(e.name_hash for e in entries)
        resolver.add("a.py")
        out = self.root / "out"
        with contextlib.redirect_stderr(io.StringIO()):
            summary = unpack.process_archive(self.archive, entries, self.info, resolver, out)
        self.assertEqual(summary["verified"], 3)
        self.assertEqual(summary["named"], 2)  # b.py recovered from a.py import
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertEqual((out / "files/a.py").read_bytes(), self.items[0][1])
        self.assertEqual((out / "files/b.py").read_bytes(), self.items[1][1])
        self.assertEqual((out / manifest["entries"][2]["output"]).read_bytes(), b"")
        self.assertFalse(list(self.root.glob(".alt2-unpack-*")))

    def test_unknown_files_get_content_based_extension(self):
        # empty.txt stays unnamed; it must keep a type label instead of a
        # misleading .bin (empty content is labelled "empty" -> .bin).
        entries = unpack.read_index(self.archive)
        out = self.root / "out"
        with contextlib.redirect_stderr(io.StringIO()):
            summary = unpack.process_archive(self.archive, entries, self.info,
                                             unpack.NameResolver(e.name_hash for e in entries), out)
        self.assertEqual(summary["unknown"], 1)
        self.assertEqual(summary["unknown_types"], {"empty": 1})
        manifest = json.loads((out / "manifest.json").read_text())
        record = manifest["entries"][2]
        self.assertEqual(record["detected_type"], "empty")
        self.assertTrue(record["output"].startswith("unknown/0002_"))
        self.assertTrue(record["output"].endswith(".bin"))

    def test_generation_recovers_name_inside_extract(self):
        # The directory lives in one payload and the bare basename in another;
        # extraction must pair them during the generation phase. The two files
        # whose names are referenced nowhere stay under unknown/ with content
        # labels instead of a misleading .bin.
        tga_header = bytes([0, 0, 2]) + b"\x00" * 9 + bytes([0x20, 0, 0x20, 0, 32]) + b"\x00" * 8
        items = [("dirs.py", b'BASE = "tree/board/"\n', False),
                 ("page.txt", b'img src="top.tga"\n', False),
                 ("tree/board/top.tga", tga_header, False)]
        self.archive.write_bytes(archive_bytes(items))
        entries = unpack.read_index(self.archive)
        out = self.root / "generated"
        with contextlib.redirect_stderr(io.StringIO()):
            summary = unpack.process_archive(self.archive, entries, self.info,
                                             unpack.NameResolver(e.name_hash for e in entries), out)
        self.assertEqual(summary["named"], 1)
        self.assertEqual(summary["unknown_types"], {"py": 1, "txt": 1})
        self.assertTrue((out / "files/tree/board/top.tga").read_bytes(), tga_header)
        unknown = sorted(p.name for p in (out / "unknown").iterdir())
        self.assertEqual([p.rsplit(".", 1)[1] for p in unknown], ["py", "txt"])

    def test_unknown_binary_without_references(self):
        payload = bytes(range(1, 40))
        items = [("opaque.bin", payload, False)]
        self.archive.write_bytes(archive_bytes(items))
        entries = unpack.read_index(self.archive)
        out = self.root / "opaque"
        with contextlib.redirect_stderr(io.StringIO()):
            summary = unpack.process_archive(self.archive, entries, self.info,
                                             unpack.NameResolver(e.name_hash for e in entries), out)
        self.assertEqual(summary["named"], 0)
        self.assertEqual(summary["unknown_types"].get("bin"), 1)
        unknown = list((out / "unknown").iterdir())
        self.assertEqual(len(unknown), 1)
        self.assertTrue(unknown[0].name.endswith(".bin"))

    def test_no_overwrite(self):
        entries = unpack.read_index(self.archive)
        out = self.root / "out"
        out.mkdir()
        (out / "sentinel").write_text("keep")
        with self.assertRaisesRegex(unpack.UnpackError, "already exists"):
            unpack.process_archive(self.archive, entries, self.info, unpack.NameResolver([]), out)
        self.assertEqual((out / "sentinel").read_text(), "keep")

    def test_symlink_output_rejected(self):
        out = self.root / "link"
        try:
            out.symlink_to(self.root / "nonexistent", target_is_directory=True)
        except OSError:
            self.skipTest("Symlinks unavailable")
        with self.assertRaisesRegex(unpack.UnpackError, "already exists"):
            unpack.process_archive(self.archive, unpack.read_index(self.archive), self.info,
                                   unpack.NameResolver([]), out)

    def test_no_partial_output_on_failure(self):
        data = archive_bytes(self.items)
        # Corrupt the second record, after one payload has already been staged.
        second = 28 + struct.unpack_from("<I", data, 8)[0]
        data[second + 8] ^= 1
        self.archive.write_bytes(data)
        out = self.root / "out"
        with self.assertRaises(unpack.UnpackError):
            unpack.process_archive(self.archive, unpack.read_index(self.archive), self.info,
                                   unpack.NameResolver([]), out)
        self.assertFalse(out.exists())
        self.assertFalse(list(self.root.glob(".alt2-unpack-*")))

    def test_verify_writes_nothing(self):
        with contextlib.redirect_stderr(io.StringIO()):
            result = unpack.process_archive(self.archive, unpack.read_index(self.archive),
                                            self.info, unpack.NameResolver([]), None)
        self.assertEqual(result["verified"], 3)
        self.assertEqual(list(self.root.iterdir()), [self.archive])


class NameTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(unpack.name_hash("ASSASSIN_M.MSM"), 0x6E2DEEFD)
        self.assertEqual(unpack.name_hash("UI\\A.PY"), unpack.name_hash("ui/a.py"))

    def test_traversal_and_windows_hazards(self):
        for name in ("../a", "/etc/passwd", "a/../../b", "\\\\host\\file", "a//b", "c:foo",
                     "a\x00b", "a/CON.txt", "a/x.", "a/../b", "x:stream", "a/./b", ""):
            with self.subTest(name=name), self.assertRaises(unpack.UnpackError):
                unpack.safe_relative_name(name)
        self.assertEqual(unpack.safe_relative_name("D:\\ymir work\\a.tga").as_posix(), "_drives/d/ymir work/a.tga")

    def test_literal_import_and_directory_hints(self):
        names = ["foo.py", "bar.py", "ui/button.png", "ui/board/bg.tga"]
        resolver = unpack.NameResolver(map(unpack.name_hash, names))
        resolver.scan(b'import foo, bar\nPATH = "ui/"\nBOARD = PATH + "board/"\nx = "button.png"\ny = "bg.tga"\n')
        resolver.generate()
        for name in names:
            self.assertEqual(resolver.resolved(unpack.name_hash(name)), name)

    def test_cross_file_directory_and_fragment_generation(self):
        # The directory and the bare basename appear in different payloads;
        # only the generate() phase can pair them.
        target = unpack.name_hash("skill_tree/board/top.tga")
        resolver = unpack.NameResolver([target])
        resolver.scan(b'path = "skill_tree/board/"\n')
        self.assertIsNone(resolver.resolved(target))
        resolver.scan(b'link href="top.tga"\n')
        self.assertIsNone(resolver.resolved(target))
        resolver.generate()
        self.assertEqual(resolver.resolved(target), "skill_tree/board/top.tga")

    def test_short_stem_generation(self):
        target = unpack.name_hash("skill_tree/direction/7.tga")
        resolver = unpack.NameResolver([target])
        resolver.scan(b'dir = "skill_tree/direction/"\n')
        resolver.generate()
        self.assertEqual(resolver.resolved(target), "skill_tree/direction/7.tga")

    def test_token_extension_generation(self):
        target = unpack.name_hash("uiskyboxchanger.py")
        resolver = unpack.NameResolver([target])
        resolver.scan(b"self.handler = SkyBoxChanger()\n")
        resolver.generate()
        self.assertEqual(resolver.resolved(target), "uiskyboxchanger.py")

    def test_generation_never_names_unmatched_hashes(self):
        resolver = unpack.NameResolver([0x11223344, 0x55667788])
        resolver.scan(b'A = "ui/"\nbackground.png\nSkyBoxChanger()\n')
        resolver.generate()
        self.assertEqual(resolver.matches, {})

    def test_unsafe_matching_name_ignored(self):
        resolver = unpack.NameResolver([unpack.name_hash("../bad.py")])
        resolver.add("../bad.py")
        self.assertFalse(resolver.matches)

    def test_ambiguous_crc_not_arbitrarily_named(self):
        resolver = unpack.NameResolver([123])
        resolver.matches[123] = {"a.py", "b.py"}
        self.assertIsNone(resolver.resolved(123))

    def test_static_hints_do_not_evaluate_code(self):
        data = b'A = "ui/"\nB = A + "board/"\nC = __import__("os").system("bad")\nD = C + "x/"\n'
        self.assertEqual(list(unpack.static_string_hints(data)), ["ui/", "ui/board/"])


class DetectTypeTests(unittest.TestCase):
    def test_magic_signatures(self):
        cases = [
            (b"\x89PNG\r\n\x1a\n" + b"\x00" * 16, "png"),
            (b"DDS |\x00\x00\x00" + b"\x00" * 16, "dds"),
            (b"\xff\xd8\xff\xe0" + b"\x00" * 16, "jpg"),
            (b"RIFF\x24\x00\x00\x00AVI LIST" + b"\x00" * 16, "avi"),
            (b"RIFF\x24\x00\x00\x00WAVEfmt " + b"\x00" * 16, "wav"),
            (b"RIFF\x24\x00\x00\x00XXXX" + b"\x00" * 16, "riff"),
            (b"OggS\x00\x02" + b"\x00" * 16, "ogg"),
            (b"Granny2 31\x00" + b"\x00" * 16, "gr2"),
            (b"\x00\x01\x00\x00\x00" + b"\x00" * 16, "ttf"),
            (b"BM\x36\x00\x00\x00" + b"\x00" * 16, "bmp"),
            (b"", "empty"),
            (b"\x00\x01\x02\x03\x7f\x80\xff" * 3, "bin"),
        ]
        for data, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(unpack.detect_content_type(data), expected)

    def test_tga_footer_and_header(self):
        self.assertEqual(unpack.detect_content_type(b"\x00" * 32 + b"TRUEVISION-XFILE.\x00"), "tga")
        header = bytes([0, 0, 2]) + b"\x00" * 9 + bytes([0x20, 0, 0x20, 0, 32]) + b"\x00" * 8
        self.assertEqual(unpack.detect_content_type(header), "tga")
        # Implausible width/height must not be reported as TGA.
        bad = bytes([0, 0, 2]) + b"\x00" * 9 + bytes([0xF0, 0xFF, 0xF0, 0xFF, 32]) + b"\x00" * 8
        self.assertNotEqual(unpack.detect_content_type(bad), "tga")

    def test_text_kinds(self):
        self.assertEqual(unpack.detect_content_type(b"import app\r\nimport ui\r\n"), "py")
        self.assertEqual(unpack.detect_content_type(b"CHAT_RGB_TALK = (255, 255, 255)\r\n"), "py")
        self.assertEqual(unpack.detect_content_type(b'<?xml version="1.0" encoding="UTF-8"?>\n<a/>\n'), "xml")
        self.assertEqual(unpack.detect_content_type(b"ScriptType RaceDataScript\r\nBaseModelFileName x\r\n"), "msm")
        self.assertEqual(unpack.detect_content_type(b"ScriptType RaceDataScript\r\nMotionFileName y\r\n"), "msa")
        self.assertEqual(unpack.detect_content_type(b"just some release notes\r\n"), "txt")
        self.assertEqual(unpack.detect_content_type(b"\x00\x01binary gibberish\r\n"), "bin")


@unittest.skipUnless((unpack.HERE / "metin2client.exe").exists() and (unpack.HERE / "data/root").exists(),
                     "Supplied ALT2 files not present")
class SuppliedFileTests(unittest.TestCase):
    def test_key_and_index(self):
        info = unpack.discover_key((unpack.HERE / "metin2client.exe").read_bytes())
        self.assertEqual(info["key_hex"], KEY.hex())
        entries = unpack.read_index(unpack.HERE / "data/root")
        self.assertEqual(len(entries), 894)
        self.assertEqual(sum(e.original_size for e in entries), 52614417)

    def test_first_file(self):
        archive = unpack.HERE / "data/root"
        with archive.open("rb") as stream:
            data = unpack.decode_entry(stream, unpack.read_index(archive)[0], KEY)
        self.assertEqual(len(data), 79675)
        self.assertTrue(data.startswith(b"ScriptType            RaceDataScript\r\n"))

    @unittest.skipUnless(os.environ.get("ALT2_FULL_TEST") == "1", "Set ALT2_FULL_TEST=1 to verify all 894 payloads")
    def test_all_files(self):
        archive = unpack.HERE / "data/root"
        with archive.open("rb") as stream:
            for entry in unpack.read_index(archive):
                with self.subTest(entry=entry.index):
                    unpack.decode_entry(stream, entry, KEY)


if __name__ == "__main__":
    unittest.main()
