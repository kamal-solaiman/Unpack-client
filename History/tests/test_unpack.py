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


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        self.pack = self.root / "sample.d2"
        self.source = [b"# test\n" * 1000, b"\x03\xf3\r\nbytecode" * 50]
        self.make_pack()

    def make_pack(self):
        from Crypto.Cipher import AES
        import lz4.block
        import xxhash
        self.key = bytes(range(32))
        self.iv = bytes(range(32, 64))
        buf = bytearray(struct.pack("<I", unpack.MAGIC) + self.key + self.iv)
        for i, content in enumerate(self.source):
            compressed = lz4.block.compress(content, store_size=False)
            if i == 1:  # uncompressed entries are still AES-CFB encrypted
                compressed = content
            checksum = xxhash.xxh32(content, seed=unpack.MAGIC).intdigest()
            buf.extend(unpack.HEADER.pack(len(content), checksum, len(buf) + 20,
                                          len(compressed), 0x12345678 + i))
            buf.extend(AES.new(self.key, AES.MODE_CFB, iv=self.iv[:16],
                               segment_size=128).encrypt(compressed))
        self.pack.write_bytes(buf)

    def test_index_and_decode(self):
        key, iv, entries = unpack.read_index(self.pack)
        self.assertEqual((key, iv), (self.key, self.iv))
        self.assertEqual(len(entries), 2)
        with self.pack.open("rb") as src:
            self.assertEqual([unpack.decode(src, e, key, iv) for e in entries], self.source)

    def test_extract_manifest_and_no_overwrite(self):
        out = self.root / "nested" / "output"
        self.assertEqual(unpack.run(self.pack, out, 1_000_000, 1_000_000),
                         (2, sum(map(len, self.source))))
        self.assertEqual((out / "0000_12345678.py").read_bytes(), self.source[0])
        self.assertEqual((out / "0001_12345679.pyc").read_bytes(), self.source[1])
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertEqual(manifest["entries"][1]["sha256"], hashlib.sha256(self.source[1]).hexdigest())
        with self.assertRaises(unpack.UnpackError):
            unpack.run(self.pack, out, 1_000_000, 1_000_000)

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

    @unittest.skipUnless(os.environ.get("HISTORY_FULL_TEST") == "1", "opt-in sample integration test")
    def test_supplied_sample(self):
        sample = unpack.HERE / "pack/workplace.d2"
        key, iv, entries = unpack.read_index(sample)
        self.assertEqual(len(entries), 813)
        self.assertEqual(unpack.client_fingerprint(unpack.HERE / "History2.exe"), unpack.CLIENT_SHA256)
        self.assertEqual(unpack.run(sample, None, unpack.DEFAULT_FILE_LIMIT, unpack.DEFAULT_TOTAL_LIMIT),
                         (813, 16929395))


if __name__ == "__main__":
    unittest.main()
