"""Synthetic fixtures plus optional integration test against the supplied sample."""
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import unpack


def build_pack(path: Path, sources, hashes=None):
    from Crypto.Cipher import AES
    import lz4.block
    import xxhash
    key = bytes(range(32))
    iv = bytes(range(32, 64))
    buf = bytearray(struct.pack("<I", unpack.MAGIC) + key + iv)
    for i, content in enumerate(sources):
        compressed = lz4.block.compress(content, store_size=False)
        if not content.startswith(b"\x03\xf3\r\n") and len(compressed) >= len(content):
            compressed = content  # uncompressed entries are still AES-CFB encrypted
        checksum = xxhash.xxh32(content, seed=unpack.MAGIC).intdigest()
        name_hash = hashes[i] if hashes else 0x12345678 + i
        buf.extend(unpack.HEADER.pack(len(content), checksum, len(buf) + 20,
                                      len(compressed), name_hash))
        buf.extend(AES.new(key, AES.MODE_CFB, iv=iv[:16],
                           segment_size=128).encrypt(compressed))
    path.write_bytes(buf)


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        self.pack = self.root / "sample.d2"
        self.source = [b"# test\n" * 1000, b"\x03\xf3\r\nbytecode" * 50]
        build_pack(self.pack, self.source)

    def test_index_and_decode(self):
        key, iv, entries = unpack.read_index(self.pack)
        self.assertEqual((key, iv), (bytes(range(32)), bytes(range(32, 64))))
        self.assertEqual(len(entries), 2)
        with self.pack.open("rb") as src:
            self.assertEqual([unpack.decode(src, e, key, iv) for e in entries], self.source)

    def test_extract_manifest_and_no_overwrite(self):
        out = self.root / "nested" / "output"
        self.assertEqual(unpack.run(self.pack, out, 1_000_000, 1_000_000),
                         (2, sum(map(len, self.source)), 0))
        # No hints exist for this synthetic pack: content stays verified but unnamed.
        self.assertEqual((out / "unknown" / "0000_12345678.py").read_bytes(), self.source[0])
        self.assertEqual((out / "unknown" / "0001_12345679.pyc").read_bytes(), self.source[1])
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertEqual(manifest["entries"][1]["sha256"], hashlib.sha256(self.source[1]).hexdigest())
        self.assertIsNone(manifest["entries"][0]["name"])
        self.assertEqual(manifest["named"], 0)
        with self.assertRaises(unpack.UnpackError):
            unpack.run(self.pack, out, 1_000_000, 1_000_000)

    def test_name_recovery_from_content_and_sibling(self):
        # Entry 0 references its own name; entry 1 is bytecode paired with it.
        hashes = [unpack.name_hash("root/sample.py"), unpack.name_hash("root/sample.pyc")]
        pack = self.root / "named.d2"
        build_pack(pack, [b'PATH = "root/sample.py"\n# x\n', b"\x03\xf3\r\ncode"], hashes)
        out = self.root / "named-out"
        unpack.run(pack, out, 1_000_000, 1_000_000)
        self.assertEqual((out / "files" / "root" / "sample.py").read_bytes(),
                         b'PATH = "root/sample.py"\n# x\n')
        self.assertEqual((out / "files" / "root" / "sample.pyc").read_bytes(),
                         b"\x03\xf3\r\ncode")
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertEqual(manifest["named"], 2)
        self.assertEqual(manifest["entries"][1]["name"], "root/sample.pyc")

    def test_name_recovery_from_names_file(self):
        pack = self.root / "listed.d2"
        hashes = [unpack.name_hash("listed.py")]
        build_pack(pack, [b"# nothing points at this name\n"], hashes)
        names = self.root / "names.txt"
        names.write_text("# comment\nlisted.py\nnot-in-archive.py\n", encoding="utf-8")
        _, _, entries = unpack.read_index(pack)
        resolver = unpack.build_resolver(entries, client=None, name_files=[names])
        out = self.root / "listed-out"
        unpack.run(pack, out, 1_000_000, 1_000_000, resolver=resolver)
        self.assertEqual((out / "files" / "listed.py").read_bytes(),
                         b"# nothing points at this name\n")

    def test_corruption_is_not_published(self):
        data = bytearray(self.pack.read_bytes())
        data[unpack.FIRST_ENTRY + 24] ^= 0xff
        self.pack.write_bytes(data)
        out = self.root / "output"
        with self.assertRaises(unpack.UnpackError):
            unpack.run(self.pack, out, 1_000_000, 1_000_000)
        self.assertFalse(out.exists())

    def test_reject_bad_offset_and_truncated_record(self):
        original = self.pack.read_bytes()
        data = bytearray(original)
        struct.pack_into("<I", data, unpack.FIRST_ENTRY + 8, 0x1234)
        self.pack.write_bytes(data)
        with self.assertRaises(unpack.UnpackError):
            unpack.read_index(self.pack)
        self.pack.write_bytes(original[:-1])
        with self.assertRaises(unpack.UnpackError):
            unpack.read_index(self.pack)

    def test_limits_and_wrong_key(self):
        with self.assertRaises(unpack.UnpackError):
            unpack.read_index(self.pack, max_file_size=10)
        with self.assertRaises(unpack.UnpackError):
            unpack.read_index(self.pack, max_total_size=7200)
        key, iv, entries = unpack.read_index(self.pack)
        with self.pack.open("rb") as src, self.assertRaises(unpack.UnpackError):
            unpack.decode(src, entries[0], b"x" * 32, iv)


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        self.packdir = self.root / "pack"
        self.packdir.mkdir()
        for name in ("workplace.d2", "icon.d2", "locale.d2"):
            (self.packdir / name).write_bytes(b"x")

    def test_single_pack_needs_no_selection(self):
        single = self.root / "solo"
        single.mkdir()
        (single / "only.d2").write_bytes(b"x")
        self.assertEqual([p.name for p in unpack.select_packs(single)], ["only.d2"])
        # an explicit file path is taken as-is, never prompted
        self.assertEqual(unpack.select_packs(self.packdir / "icon.d2"),
                         [self.packdir / "icon.d2"])

    def test_non_terminal_requires_flags(self):
        with self.assertRaises(unpack.UnpackError) as ctx:
            unpack.select_packs(self.packdir, interactive=False)
        self.assertIn("--all", str(ctx.exception))
        self.assertEqual([p.name for p in unpack.select_packs(self.packdir, all_=True)],
                         ["icon.d2", "locale.d2", "workplace.d2"])
        self.assertEqual([p.name for p in unpack.select_packs(self.packdir, files=["WORKPLACE"])],
                         ["workplace.d2"])
        with self.assertRaises(unpack.UnpackError):
            unpack.select_packs(self.packdir, files=["missing"])

    def test_prompt_specific_pack_or_all(self):
        answer = iter(["0", "3\n1"])
        chosen = unpack.select_packs(self.packdir, interactive=True,
                                     input_fn=lambda: next(answer))
        self.assertEqual([p.name for p in chosen], ["workplace.d2", "icon.d2"])
        chosen = unpack.select_packs(self.packdir, interactive=True, input_fn=lambda: "a")
        self.assertEqual(len(chosen), 3)
        with self.assertRaises(unpack.UnpackError):
            unpack.select_packs(self.packdir, interactive=True,
                                input_fn=lambda: (_ for _ in ()).throw(EOFError))

    def test_output_rules(self):
        pack = self.packdir / "workplace.d2"
        default = unpack.HERE / "unpacked" / "workplace"
        explicit = self.root / "out"
        self.assertEqual(unpack.output_for(pack, 1, None), default)
        self.assertEqual(unpack.output_for(pack, 1, explicit), explicit)
        self.assertEqual(unpack.output_for(pack, 3, None), unpack.HERE / "unpacked" / "workplace")
        self.assertEqual(unpack.output_for(pack, 3, explicit), explicit / "workplace")

    def test_directory_without_packs(self):
        empty = self.root / "empty"
        empty.mkdir()
        with self.assertRaises(unpack.UnpackError):
            unpack.select_packs(empty)
        with self.assertRaises(unpack.UnpackError):
            unpack.select_packs(self.root / "nope.d2")


class FullSampleTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("HISTORY_FULL_TEST") == "1", "opt-in sample integration test")
    def test_supplied_sample(self):
        import shutil
        sample = unpack.HERE / "pack" / "workplace.d2"
        key, iv, entries = unpack.read_index(sample)
        self.assertEqual(len(entries), 813)
        self.assertEqual(unpack.client_fingerprint(unpack.HERE / "History2.exe"), unpack.CLIENT_SHA256)
        self.assertEqual(unpack.run(sample, None, unpack.DEFAULT_FILE_LIMIT, unpack.DEFAULT_TOTAL_LIMIT),
                         (813, 16929395, 0))
        out = unpack.HERE / "unpacked" / "full-test-output"
        if out.exists():
            shutil.rmtree(out)
        resolver = unpack.build_resolver(entries, unpack.HERE / "History2.exe")
        count, total, named = unpack.run(sample, out, unpack.DEFAULT_FILE_LIMIT,
                                         unpack.DEFAULT_TOTAL_LIMIT, resolver=resolver)
        try:
            self.assertEqual((count, total), (813, 16929395))
            self.assertEqual(named, 813)  # every entry restored to its real name and path
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["named"], 813)
            outputs = {e["output"] for e in manifest["entries"]}
            self.assertIn("files/colorinfo.py", outputs)
            self.assertIn("files/uiscript/gamewindow.pyc", outputs)
            self.assertIn("files/ui_fundamentals.md", outputs)
            self.assertFalse(any(o.startswith("unknown/") for o in outputs))
            # folder layout is restored, not a flat dump
            self.assertTrue((out / "files" / "uiscript").is_dir())
        finally:
            shutil.rmtree(out)


class RecoveryTests(unittest.TestCase):
    """Damaged/truncated packs: strict errors stay loud, --keep-going salvages."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        self.pack = self.root / "multi.d2"
        self.source = [(f"# file {i}\nprint({i})\n".encode() * 200) for i in range(6)]
        build_pack(self.pack, self.source)

    def test_strict_truncated_tail_reports_offsets(self):
        _, _, entries = unpack.read_index(self.pack)
        cut = entries[4].data_offset + 10
        bad = self.root / "trunc.d2"
        bad.write_bytes(self.pack.read_bytes()[:cut])
        with self.assertRaises(unpack.UnpackError) as ctx:
            unpack.read_index(bad)
        message = str(ctx.exception)
        self.assertIn("truncated payload in record 4", message)
        self.assertIn("0x", message)  # offsets and sizes for diagnosis
        self.assertIn("incomplete download", message)
        self.assertIn("--keep-going", message)

    def test_keep_going_salvages_truncated_tail(self):
        _, _, entries = unpack.read_index(self.pack)
        cut = entries[4].data_offset + 10
        bad = self.root / "trunc.d2"
        bad.write_bytes(self.pack.read_bytes()[:cut])
        index = unpack.read_index_full(bad, keep_going=True)
        self.assertEqual([e.index for e in index.entries], [0, 1, 2, 3])
        self.assertEqual([b.index for b in index.broken], [4])
        out = self.root / "out"
        result = unpack._run(bad, out, 1_000_000, 100_000_000, keep_going=True)
        self.assertEqual((result.ok, result.total, result.broken, result.failed), (4, 5, 1, 0))
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertEqual(manifest["broken"], 1)
        self.assertEqual([(e["index"], e["status"]) for e in manifest["entries"]],
                         [(0, "ok"), (1, "ok"), (2, "ok"), (3, "ok"), (4, "broken")])
        self.assertIsNone(manifest["entries"][4]["output"])
        self.assertIn("truncated payload", manifest["entries"][4]["error"])
        # The salvageable prefix is really on disk and byte-identical.
        self.assertEqual((out / "unknown" / "0000_12345678.py").read_bytes(), self.source[0])

    def test_keep_going_resyncs_past_corrupt_middle_header(self):
        _, _, entries = unpack.read_index(self.pack)
        data = bytearray(self.pack.read_bytes())
        struct.pack_into("<I", data, entries[2].header_offset + 12, 0xFFFFFFF0)
        bad = self.root / "bad.d2"
        bad.write_bytes(data)
        with self.assertRaises(unpack.UnpackError):
            unpack.read_index(bad)
        index = unpack.read_index_full(bad, keep_going=True)
        self.assertEqual([e.index for e in index.entries], [0, 1, 3, 4, 5])
        self.assertEqual([b.index for b in index.broken], [2])
        self.assertTrue(any("Re-synced" in w for w in index.warnings))
        out = self.root / "out"
        result = unpack._run(bad, out, 1_000_000, 100_000_000, keep_going=True)
        self.assertEqual((result.ok, result.broken), (5, 1))
        self.assertEqual((out / "unknown" / "0005_1234567d.py").read_bytes(), self.source[5])

    def test_zero_terminator_record(self):
        data = self.pack.read_bytes() + b"\x00" * 20
        pack = self.root / "term.d2"
        pack.write_bytes(data)
        with self.assertRaises(unpack.UnpackError) as ctx:
            unpack.read_index(pack)
        self.assertIn("--keep-going", str(ctx.exception))
        index = unpack.read_index_full(pack, keep_going=True)
        self.assertEqual(len(index.entries), 6)
        self.assertEqual(index.broken, [])
        out = self.root / "out"
        result = unpack._run(pack, out, 1_000_000, 100_000_000, keep_going=True)
        self.assertEqual((result.ok, result.total), (6, 6))

    def test_failed_payload_is_recorded_not_fatal(self):
        _, _, entries = unpack.read_index(self.pack)
        data = bytearray(self.pack.read_bytes())
        data[entries[1].data_offset + 5] ^= 0xFF
        bad = self.root / "corrupt.d2"
        bad.write_bytes(data)
        out = self.root / "out"
        result = unpack._run(bad, out, 1_000_000, 100_000_000, keep_going=True)
        self.assertEqual((result.ok, result.failed), (5, 1))
        manifest = json.loads((out / "manifest.json").read_text())
        row = [e for e in manifest["entries"] if e["index"] == 1][0]
        self.assertEqual(row["status"], "failed")
        self.assertIsNone(row["output"])
        self.assertTrue(all(e["status"] == "ok" for e in manifest["entries"] if e["index"] != 1))

    def test_forward_gap_padding_warns_and_accepts(self):
        # Insert 16 padding bytes before the LAST payload; only its data_offset changes.
        _, _, entries = unpack.read_index(self.pack)
        last = entries[-1]
        raw = self.pack.read_bytes()
        gap = 16
        patched = bytearray(raw[:last.header_offset + 8]
                            + struct.pack("<I", last.data_offset + gap)
                            + raw[last.header_offset + 12:last.data_offset]
                            + b"\x00" * gap + raw[last.data_offset:])
        pack = self.root / "gap.d2"
        pack.write_bytes(patched)
        with self.assertRaises(unpack.UnpackError):
            unpack.read_index(pack)
        index = unpack.read_index_full(pack, keep_going=True)
        self.assertEqual(len(index.entries), 6)
        self.assertTrue(any("padding bytes" in w for w in index.warnings))

    def test_cli_keep_going_exit_code_and_partial_output(self):
        _, _, entries = unpack.read_index(self.pack)
        cut = entries[4].data_offset + 10
        bad = self.root / "trunc.d2"
        bad.write_bytes(self.pack.read_bytes()[:cut])
        out = self.root / "cli-out"
        code = unpack.main(["extract", str(bad), "-o", str(out), "--keep-going",
                            "--client", str(self.root / "no-client.exe")])
        self.assertEqual(code, 1)  # published partial output, but signals incompleteness
        self.assertTrue((out / "manifest.json").is_file())
        self.assertEqual(len(list((out / "unknown").iterdir())), 4)


class SniffingTests(unittest.TestCase):
    def test_extension_table(self):
        cases = {
            b"\x03\xf3\r\ncode": ".pyc",
            b"\x89PNG\r\n\x1a\n....": ".png",
            b"\xff\xd8\xff\xe0....": ".jpg",
            b"GIF89a....": ".gif",
            b"BM....": ".bmp",
            b"DDS |...": ".dds",
            b"\x00\x00\x01\x00....": ".ico",
            b"OggS....": ".ogg",
            b"ID3....": ".mp3",
            b"RIFF\x00\x00\x00\x00WAVE": ".wav",
            b"RIFF\x00\x00\x00\x00AVI ": ".avi",
            b'"""docstring-led module\nimport os\n': ".py",
            b"BTN = \"x\"\nimport ui\n": ".py",
            b"<?xml version='1.0'?><a/>": ".xml",
            b"<atlas><img/></atlas>": ".xml",
            b'{"a": 1}': ".json",
            b"hello world\nplain text file\n": ".txt",
            b"\x00\x01\x02\xff\xfe binary": ".bin",
        }
        for raw, want in cases.items():
            with self.subTest(raw=raw[:12]):
                self.assertEqual(unpack.extension(raw), want)
        tga = b"\x00" * 100 + b"TRUEVISION-XFILE.\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        self.assertEqual(unpack.extension(tga), ".tga")


class ResolverExtraTests(unittest.TestCase):
    def test_quoted_stem_plus_asset_extension(self):
        # Payload references icon/item/001 with no extension; entry is the .png.
        wanted = "icon/item/001.png"
        resolver = unpack.NameResolver([unpack.name_hash(wanted)])
        resolver.scan(b'img = LoadImage("icon/item/001")\n' * 10)
        resolver.finalize()
        self.assertEqual(resolver.resolved(unpack.name_hash(wanted)), wanted)

    def test_basename_times_directory_combination(self):
        # Directory and basename appear in different places; joined they match.
        wanted = "uiscript/gamewindow.py"
        resolver = unpack.NameResolver([unpack.name_hash(wanted)])
        resolver.scan(b'// see gamewindow.py for layout\nPATH = "uiscript/"\n')
        resolver.finalize()
        self.assertEqual(resolver.resolved(unpack.name_hash(wanted)), wanted)

    def test_unknown_reason_messages(self):
        resolver = unpack.NameResolver([0x11111111, 0x22222222])
        self.assertIn("--names", resolver.unknown_reason(0x11111111))
        resolver.matches[0x22222222] = {"a.py", "b.py"}
        self.assertIn("ambiguous", resolver.unknown_reason(0x22222222))

    def test_hints_directory_recovers_asset_name(self):
        wanted = "d:/ymir work/ui/game/image.sub"
        hashed = unpack.name_hash(wanted)
        with tempfile.TemporaryDirectory() as tmp:
            hints = Path(tmp) / "extracted-text-pack"
            hints.mkdir()
            (hints / "ref.py").write_text('IMG = "d:/ymir work/ui/game/image.sub"\n')
            entry = unpack.Entry(0, 68, 10, 0, 88, 10, hashed)
            resolver = unpack.build_resolver([entry], client=None, hint_paths=[hints])
            resolver.finalize()
        self.assertEqual(resolver.resolved(hashed), wanted)

    def test_manifest_marks_status_and_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "s.d2"
            build_pack(pack, [b"# lone\n" * 500])
            out = root / "out"
            unpack.run(pack, out, 1_000_000, 1_000_000)
            manifest = json.loads((out / "manifest.json").read_text())
            row = manifest["entries"][0]
            self.assertEqual(row["status"], "ok")
            self.assertIsNone(row["name"])
            self.assertIn("unknown_reason", row)


if __name__ == "__main__":
    unittest.main()
