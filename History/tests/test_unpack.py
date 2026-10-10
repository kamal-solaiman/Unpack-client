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


if __name__ == "__main__":
    unittest.main()
