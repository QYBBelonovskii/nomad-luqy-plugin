import logging

from nomad.datamodel import EntryArchive

from nomad_luqy_plugin.parsers.parser import LuQYParser


def test_parse_file():
    parser = LuQYParser()
    archive = EntryArchive()
    parser.parse('tests/data/GaAs013_largeSpot.txt', archive, logging.getLogger())

    assert archive.data is not None
    assert hasattr(archive.data, 'times')
    assert len(archive.data.times) > 0

    assert hasattr(archive.data, 'wavelength')
    assert len(archive.data.wavelength) > 0

    assert hasattr(archive.data, 'lum_flux_density')
    assert archive.data.lum_flux_density.shape[0] == len(archive.data.wavelength)
