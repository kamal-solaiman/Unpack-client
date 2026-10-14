"""Optional stdlib-only integration test for the repository's History fixture.

Usage: integration.py <HistoryUnpacker executable> <archive.d2> [more archives...]

The first archive is the repository fixture. Extra arguments (when supplied by
CTest) are additional D2 archives used to exercise multi-archive batches.
"""
import csv
import hashlib
import pathlib
import shutil
import subprocess
import sys
import tempfile

exe, *archives = (pathlib.Path(p).resolve() for p in sys.argv[1:])
archive = archives[0]
extra = archives[1:]


def run(*args, expected=0):
    result = subprocess.run([str(exe), *map(str, args)], capture_output=True, text=True)
    if result.returncode != expected:
        raise AssertionError((result.returncode, result.stdout, result.stderr))
    return result.stdout


def manifest_rows(path):
    with pathlib.Path(path).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


with tempfile.TemporaryDirectory(prefix='history-integration-') as directory:
    root = pathlib.Path(directory)

    # --- single archive ---------------------------------------------------
    assert 'Verified: 813; failed: 0' in run('--archive', archive, 'verify')
    out = run('--archive', archive, '--out', root / 'all', '--include-unresolved', 'all')
    folder = root / 'all' / archive.stem
    assert 'history-manifest-all.csv' in out
    rows = manifest_rows(folder / 'history-manifest.csv')
    assert len(rows) == 813
    combined = manifest_rows(root / 'all' / 'history-manifest-all.csv')
    assert len(combined) == 813
    assert {r['archive'] for r in combined} == {archive.as_posix()}
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

    run('--archive', archive, '--out', root / 'single', 'extract', 'UI.PY')
    assert (root / 'single/ui.py').read_bytes() == (folder / 'ui.py').read_bytes()
    run('--archive', archive, '--out', root / 'single', 'extract', 'ui.py', expected=1)
    run('--archive', archive, 'extract', 'this_name_does_not_exist.xyz', expected=1)
    run('--archive', archive, '--out', root / 'resolved', 'all', expected=2)

    # "manifest" writes exactly the requested CSV and no payload.
    run('--archive', archive, 'manifest', root / 'names.csv')
    assert (root / 'names.csv').exists()
    assert list(manifest_rows(root / 'names.csv')[0].keys())[:3] == ['archive', 'output_folder', 'name_crc32']
    assert not (root / archive.stem).exists()

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

    # --- directory argument / discovery ----------------------------------
    client = root / 'client'
    (client / 'pack' / 'sub').mkdir(parents=True)
    shutil.copy2(archive, client / 'pack' / 'workplace.d2')
    shutil.copy2(archive, client / 'pack' / 'sub' / 'locale_sound.d2')
    # Kept outside the scanned tree: the extension matches but the magic does not,
    # so discovery must ignore it instead of guessing.
    decoy = root / 'decoys'
    decoy.mkdir()
    (decoy / 'not-an-archive.d2').write_bytes(b'not a d2 archive at all')
    run('--archive', decoy, 'scan', expected=1)
    run('--archive', decoy / 'not-an-archive.d2', 'info', expected=1)
    scanned = run('--archive', client, 'scan')
    assert 'archives in scope: 2' in scanned
    assert 'Usable archives: 2 / 2' in scanned
    assert 'not-an-archive.d2' not in scanned
    listing = run('--archive', client, 'list')
    assert listing.count('=== ') == 2          # one section per archive
    assert listing.count('Recovered ') == 2    # names recovered for both archives
    assert 'workplace.d2' in listing and 'locale_sound.d2' in listing

    # Repeated --archive options select both copies explicitly.
    verify = run('--archive', client / 'pack' / 'workplace.d2',
                 '--archive', client / 'pack' / 'sub' / 'locale_sound.d2', 'verify')
    assert 'Verified: 1626; failed: 0; total: 1626' in verify
    assert 'Archives: 2; unreadable: 0' in verify

    # One batch extraction writes a separate folder per archive.
    batch = run('--archive', client, '--out', root / 'batch', '--include-unresolved', 'all')
    assert 'Archives: 2; Extracted: 1626' in batch
    rows = manifest_rows(root / 'batch' / 'history-manifest-all.csv')
    assert len(rows) == 1626
    assert {r['output_folder'] for r in rows} == {'workplace', 'locale_sound'}
    for row in rows:
        assert (root / 'batch' / row['output_path']).exists()
    assert (root / 'batch' / 'workplace' / 'ui.py').read_bytes() == (folder / 'ui.py').read_bytes()
    assert (root / 'batch' / 'locale_sound' / 'ui.py').read_bytes() == (folder / 'ui.py').read_bytes()

    # One corrupt archive must not stop the batch: the healthy one is still verified.
    broken = root / 'broken'
    broken.mkdir()
    shutil.copy2(archive, broken / 'good.d2')
    payload = bytearray(archive.read_bytes())
    payload[200] ^= 0xFF                       # corrupt the first entry's payload
    (broken / 'bad.d2').write_bytes(payload)
    result = run('--archive', broken, 'verify', expected=1)
    assert 'Archives: 2; unreadable: 0' in result
    assert 'Verified: 1625; failed: 1; total: 1626' in result
    assert 'Usable archives: 1 / 2' in run('--archive', broken, 'scan', expected=1)

    # --- extra fixtures supplied by CTest --------------------------------
    for path in extra:
        run('--archive', path, 'verify')
        run('--archive', path, '--out', root / ('extra-' + path.stem), '--include-unresolved', 'all')

print('All History fixture integration tests passed.')
