"""Optional stdlib-only integration test for the repository's History fixture."""
import csv
import hashlib
import pathlib
import subprocess
import sys
import tempfile

exe, archive = map(lambda p: pathlib.Path(p).resolve(), sys.argv[1:3])

def run(*args, expected=0):
    result = subprocess.run([str(exe), '--archive', str(archive), *map(str, args)],
                            capture_output=True, text=True)
    if result.returncode != expected:
        raise AssertionError((result.returncode, result.stdout, result.stderr))
    return result.stdout

with tempfile.TemporaryDirectory(prefix='history-integration-') as directory:
    root = pathlib.Path(directory)
    assert 'Verified: 813; failed: 0' in run('verify')
    run('--out', root / 'all', '--include-unresolved', 'all')
    with (root / 'all/history-manifest.csv').open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 813
    digest = hashlib.sha256()
    for row in sorted(rows, key=lambda r: int(r['name_crc32'], 16)):
        assert row['status'] in ('verified_extracted', 'verified_unresolved')
        content = (root / 'all' / row['output_path']).read_bytes()
        assert len(content) == int(row['decoded_size'])
        digest.update(int(row['name_crc32'], 16).to_bytes(4, 'little'))
        digest.update(len(content).to_bytes(8, 'little'))
        digest.update(content)
    # Independently decoded using PyCryptodome + python-lz4 + xxhash during format analysis.
    assert digest.hexdigest() == '500a48d43bd2419bc33dc194e6b3dade42afbaf8996735dfc2c53b859a782daa'
    run('--out', root / 'single', 'extract', 'UI.PY')
    assert (root / 'single/ui.py').read_bytes() == (root / 'all/ui.py').read_bytes()
    run('--out', root / 'single', 'extract', 'ui.py', expected=1)
    run('extract', 'this_name_does_not_exist.xyz', expected=1)
    run('--out', root / 'resolved', 'all', expected=2)
    corrupted = bytearray(archive.read_bytes())
    corrupted[100] ^= 0xff
    bad = root / 'corrupted.d2'
    bad.write_bytes(corrupted)
    run('--archive', bad, 'verify', expected=1)
    # Malformed entry arithmetic and truncation are rejected before decryption.
    corrupted = bytearray(archive.read_bytes()[:88])
    corrupted[76:80] = (0xffffffff).to_bytes(4, 'little')
    bad.write_bytes(corrupted)
    run('--archive', bad, 'info', expected=1)
print('All History fixture integration tests passed.')
