"""Stdlib-only integration test that needs no proprietary fixture.

Generates small valid History D2 archives with the testarchive helper into a
Metin2-style pack directory (extension-less files with arbitrary names) and
checks that HistoryUnpacker discovers, verifies and extracts every one of them.

Usage: integration_generated.py <HistoryUnpacker exe> <testarchive exe>
"""
import pathlib
import subprocess
import sys
import tempfile

exe, builder = (pathlib.Path(p).resolve() for p in sys.argv[1:3])

ARCHIVES = {
    # name: virtual entry names inside it (Metin2-style packs: names the old
    # hardcoded candidate list did not know must also be found).
    'workplace.d2': ['ui/work.py', 'uiscript/workdialog.py'],
    'root': ['root/r.py'],
    'PC': ['pc/pc.py'],
    'monster': ['monster/monster.py'],
    'locale_de': ['locale_de/l.py'],
    'sound_ambience': ['sound_ambience/s.py'],
}
NON_ARCHIVES = {'notes.txt': b'plain text\n', 'bogus.d2': b'NOPEnot an archive'}


def run(args, cwd=None, expected=0):
    result = subprocess.run([str(exe), *map(str, args)], capture_output=True, text=True, cwd=cwd)
    if result.returncode != expected:
        raise AssertionError((result.returncode, result.stdout, result.stderr))
    return result.stdout


def build(path, names, workdir):
    files = []
    for i, name in enumerate(names):
        payload = workdir / (name.replace('/', '_') + '.bin')
        # Multi-block (over 32 bytes) and non-multiple-of-16 lengths exercise the
        # CFB128 feedback chain and its final partial block.
        payload.write_bytes(bytes((0x41 + i + j) % 256 for j in range(37 + 11 * i)))
        files.append(f'{name}={payload}')
    subprocess.run([str(builder), str(path), *files], check=True, capture_output=True)


with tempfile.TemporaryDirectory(prefix='history-discovery-') as directory:
    root = pathlib.Path(directory)
    pack = root / 'client' / 'pack'
    pack.mkdir(parents=True)
    for name, entries in ARCHIVES.items():
        build(pack / name, entries, root)
    for name, content in NON_ARCHIVES.items():
        (pack / name).write_bytes(content)
    names = root / 'names.txt'
    names.write_text('\n'.join(n for ns in ARCHIVES.values() for n in ns) + '\n')

    expected_files = sorted(pack / name for name in ARCHIVES)

    # --- scan: every archive file is found by its magic, nothing else --------
    out = run(['--archive', pack, 'scan'])
    for archive in expected_files:
        assert str(archive) in out, f'{archive} not discovered'
    for name in NON_ARCHIVES:
        assert (pack / name).as_posix() not in out
    assert 'Usable archives: 6 / 6' in out

    # --- verify ---------------------------------------------------------------
    assert 'Verified: 7; failed: 0; total: 7' in run(['--archive', pack, 'verify'])

    # --- full extraction of the whole directory -------------------------------
    out = run(['--archive', pack, '--names', names, '--out', root / 'out', 'all'])
    rows_out = root / 'out'
    for name, entries in ARCHIVES.items():
        folder = rows_out / pathlib.Path(name).stem
        for entry in entries:
            extracted = folder / entry
            assert extracted.is_file(), f'missing {extracted}'
    for name in NON_ARCHIVES:
        assert not any(p.name == name for p in rows_out.rglob('*')), f'{name} leaked into output'

    # --- automatic discovery without --archive (client folder as cwd) ---------
    out = run(['scan'], cwd=root / 'client')
    assert 'Usable archives: 6 / 6' in out, out

print('Generated-fixture discovery integration passed.')
