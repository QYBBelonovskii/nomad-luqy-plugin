import numpy as np
from nomad.client import normalize_all, parse


def test_schema_package():
    entry_archive = parse('tests/data/test.archive.yaml')[0]
    normalize_all(entry_archive)

    assert entry_archive.data is not None
    meas = entry_archive.data

    if hasattr(meas, 'method') and isinstance(meas.method, str):
        assert meas.method.startswith('LuQY')

    # settings
    s = meas.settings
    assert np.isclose(s.laser_intensity.m_as('mW/cm**2'), 99.6, atol=1e-12)
    assert np.isclose(s.bias_voltage.m_as('V'), 0.0, atol=1e-12)
    assert np.isclose(s.smu_current_density.m_as('mA/cm**2'), 0.0, atol=1e-12)
    assert np.isclose(s.integration_time.m_as('ms'), 170.0, atol=1e-12)
    assert np.isclose(s.delay_time.m_as('s'), 0.0, atol=1e-12)
    assert np.isclose(s.eqe_at_laser, 0.90, atol=1e-12)
    assert np.isclose(s.laser_spot_size.m_as('cm**2'), 0.4, atol=1e-12)
    assert np.isclose(s.subcell_area.m_as('cm**2'), 1.0, atol=1e-12)
    assert s.subcell == '--'
    # timestamp
    if hasattr(s, 'timestamp') and s.timestamp:
        assert str(s.timestamp).startswith('2025-08-27')

    # results
    r = meas.results[0]
    assert np.isclose(r.luqy, 0.00489, atol=1e-12)
    assert np.isclose(r.qfls.m_as('eV'), 1.007, atol=1e-12)
    assert np.isclose(r.bandgap.m_as('eV'), 1.422, atol=1e-12)
    assert np.isclose(r.derived_jsc.m_as('mA/cm**2'), 26.806, atol=1e-12)

    wl = r.wavelength.m_as('nm')
    lf = r.luminescence_flux_density.m_as('1/(s*cm**2*nm)')
    assert wl.shape == lf.shape == (3,)
    assert np.isclose(wl[0], 550.412, atol=1e-4)
    assert np.isclose(lf[0], 0.0, atol=1e-12)
