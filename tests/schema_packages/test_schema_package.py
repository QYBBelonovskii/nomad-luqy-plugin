import numpy as np
from nomad.client import normalize_all, parse


def test_schema_package():
    entry_archive = parse('tests/data/test.archive.yaml')[0]
    normalize_all(entry_archive)

    assert entry_archive.data is not None
    meas = entry_archive.data

    # basic checks
    assert meas.method.startswith('LuQY Pro')

    # settings
    s = meas.settings
    assert np.isclose(s.laser_intensity_suns, 0.91, atol=1e-12)
    assert np.isclose(s.bias_voltage.m_as('V'), 0.0, atol=1e-12)
    assert np.isclose(s.smu_current_density.m_as('mA/cm**2'), 0.0, atol=1e-12)
    assert np.isclose(s.integration_time.m_as('ms'), 100.0, atol=1e-12)
    assert np.isclose(s.delay_time.m_as('s'), 0.0, atol=1e-12)
    assert np.isclose(s.eqe_at_laser, 0.90, atol=1e-12)
    assert np.isclose(s.laser_spot_size.m_as('cm**2'), 0.10, atol=1e-12)
    assert np.isclose(s.subcell_area.m_as('cm**2'), 1.0, atol=1e-12)
    assert s.subcell == '--'

    # results
    r = meas.results[0]
    assert np.isclose(r.luminescence_quantum_yield, 0.0677, atol=1e-12)
    assert np.isclose(r.quasi_fermi_level_splitting.m_as('eV'), 1.532, atol=1e-12)
    assert np.isclose(r.bandgap.m_as('eV'), 2.095, atol=1e-12)
    assert np.isclose(r.derived_jsc.m_as('mA/cm**2'), 10.32, atol=1e-12)

    wl = r.wavelength.m_as('nm')
    lf = r.luminescence_flux_density.m_as('1/(s*cm**2*nm)')
    rc = np.asarray(r.raw_spectrum_counts, dtype=float)
    dc = np.asarray(r.dark_spectrum_counts, dtype=float)

    assert wl.shape == lf.shape == rc.shape == dc.shape == (3,)
    assert np.isclose(wl[0], 549.5612, atol=1e-4)
    assert np.isclose(lf[0], 0.0, atol=1e-12)
    assert np.isclose(rc[0], 1501.733, atol=1e-3)
    assert np.isclose(dc[0], 1500.533, atol=1e-3)
