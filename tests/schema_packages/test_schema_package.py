import os.path

from nomad.client import normalize_all, parse


def test_schema_package():
    test_file = os.path.join('tests', 'data', 'test.archive.yaml')
    entry_archive = parse(test_file)[0]
    normalize_all(entry_archive)

    assert entry_archive.data is not None
    assert entry_archive.data.times[0].startswith('2025-')
    assert entry_archive.data.luqy_percent[0] == 1.417
