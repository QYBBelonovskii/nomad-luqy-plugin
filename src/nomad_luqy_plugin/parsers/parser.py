"""
Parser implementation for LuQY Pro absolute photoluminescence files.

"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import numpy as np
from nomad.config import config
from nomad.parsing.parser import MatchingParser

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

from nomad_luqy_plugin.schema_packages.schema_package import (
    LuQYProMeasurement,
    LuQYProResult,
    LuQYProSettings,
)

configuration = config.get_plugin_entry_point(
    'nomad_luqy_plugin.parsers:parser_entry_point'
)

FILE_RE = r'.*\.(?:txt|csv|tsv)$'
MIN_COLS = 4


def _parse_header(
    lines: list[str], logger: BoundLogger
) -> tuple[dict[str, float], dict[str, float], int]:
    """
    Parse the header of a LuQY Pro file.

    """
    header_map_settings = {
        'Laser intensity (suns)': 'laser_intensity_suns',
        'Bias Voltage (V)': 'bias_voltage',
        'SMU current density (mA/cm2)': 'smu_current_density',
        'SMU current density (mA/cm²)': 'smu_current_density',
        'Integration Time (ms)': 'integration_time',
        'Delay time (s)': 'delay_time',
        'EQE @ laser wavelength': 'eqe_at_laser',
        'Laser spot size (cm²)': 'laser_spot_size',
        'Laser spot size (cm^2)': 'laser_spot_size',
        'Subcell area (cm²)': 'subcell_area',
        'Subcell area (cm^2)': 'subcell_area',
        'Subcell': 'subcell',
    }
    header_map_result = {
        'LuQY (%)': 'luminescence_quantum_yield',
        'iVoc (V)': 'quasi_fermi_level_splitting',
        'iVoc (eV)': 'quasi_fermi_level_splitting',
        'iVoc Confidence': 'qfls_confidence',
        'Bandgap (eV)': 'bandgap',
        'Jsc (mA/cm2)': 'derived_jsc',
        'Jsc (mA/cm²)': 'derived_jsc',
    }

    settings_vals: dict[str, float | str] = {}
    result_vals: dict[str, float] = {}
    data_start_idx: int = len(lines)

    for idx, line in enumerate(lines):
        stripped = line.strip()

        if re.match(r'^-[-\\s]*$', stripped):
            data_start_idx = idx + 2
            break
        if '\t' not in line:
            continue
        key, value = line.split('\t', 1)
        key = key.strip()
        value = value.strip()
        if key in header_map_settings:
            target = header_map_settings[key]
            if target == 'subcell':
                settings_vals[target] = value
            else:
                try:
                    settings_vals[target] = float(value.replace(',', '.'))
                except ValueError:
                    logger.debug(
                        'Could not convert setting to float', key=key, value=value
                    )
        elif key in header_map_result:
            target = header_map_result[key]
            try:
                result_vals[target] = float(value.replace(',', '.'))
            except ValueError:
                logger.debug('Could not convert result to float', key=key, value=value)

    return settings_vals, result_vals, data_start_idx


def _parse_numeric_data(
    lines: list[str], start_idx: int, logger: BoundLogger
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Parse numeric spectral data from a LuQY Pro file.

    Expects columns: Wavelength (nm), Luminescence flux density (photons/s/cm²/nm),
    Raw spectrum counts, Dark spectrum counts.

    """
    wavelengths: list[float] = []
    lum_flux: list[float] = []
    raw_counts: list[float] = []
    dark_counts: list[float] = []

    if start_idx >= len(lines):
        return (
            np.zeros(0, dtype=float),
            np.zeros(0, dtype=float),
            np.zeros(0, dtype=float),
            np.zeros(0, dtype=float),
        )

    for line in lines[start_idx:]:
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split('\t') if '\t' in stripped else re.split(r'\s+', stripped)
        if len(parts) < MIN_COLS:
            continue
        try:
            wl = float(parts[0].replace(',', '.'))
            lf = float(parts[1].replace(',', '.'))
            rc = float(parts[2].replace(',', '.'))
            dc = float(parts[3].replace(',', '.'))
        except ValueError:
            logger.debug('Skipping malformed numeric row', row=line)
            continue
        wavelengths.append(wl)
        lum_flux.append(lf)
        raw_counts.append(rc)
        dark_counts.append(dc)

    return (
        np.asarray(wavelengths, dtype=float),
        np.asarray(lum_flux, dtype=float),
        np.asarray(raw_counts, dtype=float),
        np.asarray(dark_counts, dtype=float),
    )


class LuQYParser(MatchingParser):
    """
    Parser for LuQY Pro files.

    Matches files with extensions .txt, .csv, or .tsv.
    Extracts measurement settings, results, and spectral data.

    """

    def __init__(self) -> None:
        super().__init__(name='luqy_pro_parser')
        self._mainfile_name_re = re.compile(FILE_RE)

    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger: BoundLogger,
        child_archives: dict[str, EntryArchive] | None = None,
    ) -> None:
        try:
            with open(mainfile, mode='rb') as f:
                raw_bytes = f.read()
        except OSError:
            logger.error('Failed to open file', file=mainfile)
            return

        try:
            text = raw_bytes.decode('cp1252', errors='replace')
        except Exception:
            text = raw_bytes.decode('utf-8', errors='replace')
        lines = text.splitlines()
        if not lines:
            logger.warning('Empty LuQY file', file=mainfile)
            return

        settings_vals, result_vals, data_start_idx = _parse_header(lines, logger)
        wavelength, lum_flux, raw_counts, dark_counts = _parse_numeric_data(
            lines, data_start_idx, logger
        )

        meas = LuQYProMeasurement()
        meas.settings = LuQYProSettings()

        for attr, val in settings_vals.items():
            try:
                setattr(meas.settings, attr, val)
            except Exception:
                logger.debug('Unknown setting attribute', attr=attr)

        meas.results = [LuQYProResult()]
        r = meas.results[0]
        for attr, val in result_vals.items():
            try:
                setattr(r, attr, val)
            except Exception:
                logger.debug('Unknown result attribute', attr=attr)

        if wavelength.size:
            r.wavelength = wavelength
            r.luminescence_flux_density = lum_flux
            r.raw_spectrum_counts = raw_counts
            r.dark_spectrum_counts = dark_counts

        archive.data = meas
