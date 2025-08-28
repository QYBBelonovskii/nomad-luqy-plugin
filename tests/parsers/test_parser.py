import logging

import numpy as np
from nomad.datamodel import EntryArchive

from nomad_luqy_plugin.parsers.parser import LuQYParser


def test_parse_file_single_meas():
    fpath = 'tests/data/LuQY-Control Measurement Files/Power_Avg.txt'

    parser = LuQYParser()
    archive = EntryArchive()
    parser.parse(fpath, archive, logging.getLogger())

    assert archive.data is not None
    meas = archive.data
    assert getattr(meas, 'settings') is not None
    assert getattr(meas, 'results') and len(meas.results) == 1

    # check settings
    settings = meas.settings
    assert np.isclose(
        settings.laser_intensity.m_as('mW/cm**2'), 71.45, rtol=0, atol=1e-8
    )
    assert np.isclose(settings.bias_voltage.m_as('V'), 0.0, rtol=0, atol=1e-8)
    assert np.isclose(
        settings.smu_current_density.m_as('mA/cm**2'), 0.0, rtol=0, atol=1e-8
    )
    assert np.isclose(settings.integration_time.m_as('ms'), 33, rtol=0, atol=1e-8)
    assert np.isclose(settings.delay_time.m_as('s'), 0.0, rtol=0, atol=1e-8)
    assert np.isclose(settings.eqe_at_laser, 0.90, rtol=0, atol=1e-8)
    assert np.isclose(settings.laser_spot_size.m_as('cm**2'), 0.4, rtol=0, atol=1e-8)
    assert np.isclose(settings.subcell_area.m_as('cm**2'), 1.000, rtol=0, atol=1e-8)
    assert settings.subcell == '--'


def test_parse_file_multi_meas():
    fpath = 'tests/data/LuQY-Control Measurement Files/Power_Cont_sweep.txt'

    parser = LuQYParser()
    parent = EntryArchive()

    children = {'0': EntryArchive(), '1': EntryArchive(), '2': EntryArchive()}

    parser.parse(fpath, parent, logging.getLogger(), child_archives=children)

    assert parent.data is not None


"""
def test_parse_file_single_meas():
    fpath = 'tests/data/0_1_0-ecf314iynbrwtd33zkk5auyebh.txt'

    parser = LuQYParser()
    archive = EntryArchive()
    parser.parse(fpath, archive, logging.getLogger())

    assert archive.data is not None
    meas = archive.data
    assert getattr(meas, 'settings') is not None
    assert getattr(meas, 'results') and len(meas.results) == 1

    # check settings
    settings = meas.settings
    assert np.isclose(settings.laser_intensity_suns, 0.91, rtol=0, atol=1e-8)
    assert np.isclose(settings.bias_voltage.m_as('V'), 0.0, rtol=0, atol=1e-8)
    assert np.isclose(
        settings.smu_current_density.m_as('mA/cm**2'), 0.00, rtol=0, atol=1e-8
    )
    assert np.isclose(settings.integration_time.m_as('ms'), 100.0, rtol=0, atol=1e-8)
    assert np.isclose(settings.delay_time.m_as('s'), 0.0, rtol=0, atol=1e-8)
    assert np.isclose(settings.eqe_at_laser, 0.90, rtol=0, atol=1e-8)
    assert np.isclose(settings.laser_spot_size.m_as('cm**2'), 0.10, rtol=0, atol=1e-8)
    assert np.isclose(settings.subcell_area.m_as('cm**2'), 1.000, rtol=0, atol=1e-8)
    assert settings.subcell == '--'

    # check results
    res = meas.results[0]
    assert np.isclose(res.luminescence_quantum_yield, 0.0677, rtol=0, atol=1e-8)
    assert np.isclose(res.bandgap.m_as('eV'), 2.095, rtol=0, atol=1e-8)
    assert np.isclose(
        res.quasi_fermi_level_splitting.m_as('eV'), 1.532, rtol=0, atol=1e-8
    )
    assert np.isclose(res.derived_jsc.m_as('mA/cm**2'), 10.32, rtol=0, atol=1e-8)

    # check data arrays
    wl = res.wavelength.m_as('nm')
    lf = res.luminescence_flux_density.m_as('1/(s*cm**2*nm)')
    rc = np.asarray(res.raw_spectrum_counts, dtype=float)  # без единиц
    dc = np.asarray(res.dark_spectrum_counts, dtype=float)

    assert wl is not None and lf is not None and rc is not None and dc is not None
    n = len(wl)
    assert n > 0
    assert len(lf) == n
    assert len(rc) == n
    assert len(dc) == n

    # sanity-check the first data point
    assert np.isclose(wl[0], 549.5612, rtol=0, atol=1e-4)  # 5.495612E+2
    assert np.isclose(lf[0], 0.0, rtol=0, atol=1e-12)
    assert np.isclose(rc[0], 1501.733, rtol=0, atol=1e-3)
    assert np.isclose(dc[0], 1500.533, rtol=0, atol=1e-3)

"""
