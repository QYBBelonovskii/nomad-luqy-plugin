import logging

import numpy as np
from nomad.datamodel.datamodel import EntryArchive

from nomad_luqy_plugin.parsers.parser import LuQYParser

ATOL = 1e-8


def test_power_cont_sweep_2_values():
    """Minimal multi-measurement test:
    request 2 child entries and check settings in each.
    """
    fpath = 'tests/data/LuQY-Control Measurement Files/Power_Cont_sweep.txt'

    parser = LuQYParser()
    parent = EntryArchive()

    # Prepare two child archives for the first two columns
    children = {'0': EntryArchive(), '14': EntryArchive()}
    parser.parse(fpath, parent, logging.getLogger(), child_archives=children)

    # ---- child '0'
    ch = children['0'].data
    s = ch.settings
    r = ch.results[0]

    assert np.isclose(s.laser_intensity.m_as('mW/cm**2'), 0.9722, atol=ATOL)
    assert np.isclose(s.bias_voltage.m_as('V'), 0.0, atol=ATOL)
    assert np.isclose(s.smu_current_density.m_as('mA/cm**2'), 0.0, atol=ATOL)
    assert np.isclose(s.integration_time.m_as('ms'), 165.0, atol=ATOL)
    assert np.isclose(s.delay_time.m_as('s'), 0.0, atol=ATOL)
    assert np.isclose(float(s.eqe_at_laser), 0.9, atol=ATOL)
    assert np.isclose(s.laser_spot_size.m_as('cm**2'), 0.4, atol=ATOL)
    assert np.isclose(s.subcell_area.m_as('cm**2'), 1.0, atol=ATOL)
    assert s.subcell == '--'

    assert np.isclose(float(r.luqy), 0.4403, atol=ATOL)
    assert np.isclose(r.qfls.m_as('eV'), 0.8944, atol=ATOL)
    assert getattr(r, 'qfls_het', None) in (None, np.nan)
    assert np.isclose(float(r.qfls_confidence), 1.0, atol=ATOL)
    assert np.isclose(r.bandgap.m_as('eV'), 1.4226, atol=ATOL)
    assert np.isclose(r.derived_jsc.m_as('mA/cm**2'), 26.8064, atol=ATOL)

    wl = r.wavelength.m_as('nm')
    lf = r.luminescence_flux_density.m_as('1/(s*cm**2*nm)')
    assert wl.shape == (1299,)
    assert lf.shape == (1299,)

    # ---- child '14'
    ch = children['14'].data
    s = ch.settings
    r = ch.results[0]

    assert np.isclose(s.laser_intensity.m_as('mW/cm**2'), 0.7443, atol=ATOL)
    assert np.isclose(s.bias_voltage.m_as('V'), 0.0, atol=ATOL)
    assert np.isclose(s.smu_current_density.m_as('mA/cm**2'), 0.0, atol=ATOL)
    assert np.isclose(s.integration_time.m_as('ms'), 165.0, atol=ATOL)
    assert np.isclose(s.delay_time.m_as('s'), 0.0, atol=ATOL)
    assert np.isclose(float(s.eqe_at_laser), 0.9, atol=ATOL)
    assert np.isclose(s.laser_spot_size.m_as('cm**2'), 0.4, atol=ATOL)
    assert np.isclose(s.subcell_area.m_as('cm**2'), 1.0, atol=ATOL)
    assert s.subcell == '--'

    assert np.isclose(float(r.luqy), 0.4232, atol=ATOL)
    assert np.isclose(r.qfls.m_as('eV'), 0.8866, atol=ATOL)
    assert getattr(r, 'qfls_het', None) in (None, np.nan)
    assert np.isclose(float(r.qfls_confidence), 1.0, atol=ATOL)
    assert np.isclose(r.bandgap.m_as('eV'), 1.4226, atol=ATOL)
    assert np.isclose(r.derived_jsc.m_as('mA/cm**2'), 26.8064, atol=ATOL)

    wl = r.wavelength.m_as('nm')
    lf = r.luminescence_flux_density.m_as('1/(s*cm**2*nm)')
    assert wl.shape == (1299,)
    assert lf.shape == (1299,)


def test_het_avg_sweep_values_suns():
    fpath = 'tests/data/LuQY-Control Measurement Files/HET_Avg_sweep.txt'
    parser = LuQYParser()
    parent = EntryArchive()
    children = {'0': EntryArchive(), '1': EntryArchive()}
    parser.parse(fpath, parent, logging.getLogger(), child_archives=children)

    # ---- child '0'
    ch = children['0'].data
    s = ch.settings
    r = ch.results[0]

    assert np.isclose(s.laser_intensity.m_as('mW/cm**2'), 99.5, atol=ATOL)
    assert np.isclose(s.bias_voltage.m_as('V'), 0.0, atol=ATOL)
    assert np.isclose(s.smu_current_density.m_as('mA/cm**2'), 0.0, atol=ATOL)
    assert np.isclose(s.integration_time.m_as('ms'), 165.0, atol=ATOL)
    assert np.isclose(s.delay_time.m_as('s'), 0.0, atol=ATOL)
    assert np.isclose(float(s.eqe_at_laser), 0.9, atol=ATOL)
    assert np.isclose(s.laser_spot_size.m_as('cm**2'), 0.4, atol=ATOL)
    assert np.isclose(s.subcell_area.m_as('cm**2'), 1.0, atol=ATOL)
    assert s.subcell == '--'

    assert np.isclose(float(r.luqy), 0.477, atol=ATOL)
    assert np.isclose(r.qfls.m_as('eV'), 1.007, atol=ATOL)
    assert np.isclose(r.qfls_het.m_as('eV'), 1.009, atol=ATOL)
    assert np.isclose(float(r.qfls_confidence), 1.0, atol=ATOL)
    assert np.isclose(r.bandgap.m_as('eV'), 1.423, atol=ATOL)
    assert np.isclose(r.derived_jsc.m_as('mA/cm**2'), 26.806, atol=ATOL)

    wl = r.wavelength.m_as('nm')
    lf = r.luminescence_flux_density.m_as('1/(s*cm**2*nm)')
    assert wl.shape == (1299,)
    assert lf.shape == (1299,)

    # ---- child '1'
    ch = children['1'].data
    s = ch.settings
    r = ch.results[0]

    assert np.isclose(s.laser_intensity.m_as('mW/cm**2'), 88.6, atol=ATOL)
    assert np.isclose(s.bias_voltage.m_as('V'), 0.0, atol=ATOL)
    assert np.isclose(s.smu_current_density.m_as('mA/cm**2'), 0.0, atol=ATOL)
    assert np.isclose(s.integration_time.m_as('ms'), 165.0, atol=ATOL)
    assert np.isclose(s.delay_time.m_as('s'), 0.0, atol=ATOL)
    assert np.isclose(float(s.eqe_at_laser), 0.9, atol=ATOL)
    assert np.isclose(s.laser_spot_size.m_as('cm**2'), 0.4, atol=ATOL)
    assert np.isclose(s.subcell_area.m_as('cm**2'), 1.0, atol=ATOL)
    assert s.subcell == '--'

    assert np.isclose(float(r.luqy), 0.496, atol=ATOL)
    assert np.isclose(r.qfls.m_as('eV'), 1.004, atol=ATOL)
    assert np.isclose(r.qfls_het.m_as('eV'), 1.006, atol=ATOL)
    assert np.isclose(float(r.qfls_confidence), 1.0, atol=ATOL)
    assert np.isclose(r.bandgap.m_as('eV'), 1.423, atol=ATOL)
    assert np.isclose(r.derived_jsc.m_as('mA/cm**2'), 26.806, atol=ATOL)

    wl = r.wavelength.m_as('nm')
    lf = r.luminescence_flux_density.m_as('1/(s*cm**2*nm)')
    assert wl.shape == (1299,)
    assert lf.shape == (1299,)


def test_het_avg_single_values():
    fpath = 'tests/data/LuQY-Control Measurement Files/HET_Avg.txt'
    parser = LuQYParser()
    parent = EntryArchive()
    children = {'0': EntryArchive()}  # only first column
    parser.parse(fpath, parent, logging.getLogger(), child_archives=children)

    ch = children['0'].data
    s = ch.settings
    r = ch.results[0]

    assert np.isclose(s.laser_intensity.m_as('mW/cm**2'), 101.0, atol=ATOL)
    assert np.isclose(s.bias_voltage.m_as('V'), 0.0, atol=ATOL)
    assert np.isclose(s.smu_current_density.m_as('mA/cm**2'), 0.0, atol=ATOL)
    assert np.isclose(s.integration_time.m_as('ms'), 33.0, atol=ATOL)
    assert np.isclose(s.delay_time.m_as('s'), 0.0, atol=ATOL)
    assert np.isclose(float(s.eqe_at_laser), 0.9, atol=ATOL)
    assert np.isclose(s.laser_spot_size.m_as('cm**2'), 0.4, atol=ATOL)
    assert np.isclose(s.subcell_area.m_as('cm**2'), 1.0, atol=ATOL)
    assert s.subcell == '--'

    assert np.isclose(float(r.luqy), 0.4958, atol=ATOL)
    assert np.isclose(r.qfls.m_as('eV'), 1.008, atol=ATOL)
    assert np.isclose(r.qfls_het.m_as('eV'), 1.009, atol=ATOL)
    assert np.isclose(float(r.qfls_confidence), 1.0, atol=ATOL)
    assert np.isclose(r.bandgap.m_as('eV'), 1.422, atol=ATOL)
    assert np.isclose(r.derived_jsc.m_as('mA/cm**2'), 26.81, atol=ATOL)

    wl = r.wavelength.m_as('nm')
    lf = r.luminescence_flux_density.m_as('1/(s*cm**2*nm)')
    assert wl.shape == (1299,)
    assert lf.shape == (1299,)

    # In the single file with 4 columns
    rc = np.asarray(r.raw_spectrum_counts, dtype=float)
    dc = np.asarray(r.dark_spectrum_counts, dtype=float)
    assert rc.shape == (1299,)
    assert dc.shape == (1299,)
