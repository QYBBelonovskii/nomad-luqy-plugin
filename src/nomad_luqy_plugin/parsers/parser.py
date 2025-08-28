"""
Parser implementation for LuQY Pro absolute photoluminescence files.

"""

from __future__ import annotations

import os
import re
import unicodedata
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

header_map_settings: dict[str, str] = {
    'Time': 'timestamp',
    'Laser intensity (mW/cm^2)': 'laser_intensity',
    'Laser intensity (suns)': 'laser_intensity',
    'Bias Voltage (V)': 'bias_voltage',
    'Bias voltage (V)': 'bias_voltage',
    'SMU current density (mA/cm^2)': 'smu_current_density',
    'Integration Time (ms)': 'integration_time',
    'Delay time (s)': 'delay_time',
    'EQE @ laser wavelength': 'eqe_at_laser',
    'Laser spot size (cm^2)': 'laser_spot_size',
    'Subcell area (cm^2)': 'subcell_area',
    'Subcell': 'subcell',
}

header_map_result: dict[str, str] = {
    'LuQY (%)': 'luqy',
    'QFLS (eV)': 'qfls',
    'QFLS LuQY (eV)': 'qfls',
    'QFLS HET (eV)': 'qfls_het',
    'QFLS Confidence': 'qfls_confidence',
    'QFLS confidence': 'qfls_confidence',
    'Bandgap (eV)': 'bandgap',
    'Jsc (mA/cm^2)': 'derived_jsc',
}


def _canon_key(s: str) -> str:
    """
    Canonicalize a header key string.
    Removes extraneous whitespace and normalizes certain Unicode characters.

    """
    s = unicodedata.normalize('NFKC', s).replace('\u00a0', ' ')  # NBSP
    s = s.strip()
    s = (
        s.replace('cmÂ²', 'cm^2')
        .replace('cm²', 'cm^2')
        .replace('cm�', 'cm^2')
        .replace('cm**2', 'cm^2')
        .replace('cm2', 'cm^2')
        .replace('mA/cm2', 'mA/cm^2')
        .replace('mA/cm²', 'mA/cm^2')
    )
    s = re.sub(r'\s+', ' ', s)
    return s


def parse_multi(
    lines: list[str],
    logger: BoundLogger | None = None,
) -> tuple[
    list[dict[str, object]],
    list[dict[str, float]],
    np.ndarray,
    list[np.ndarray],
    list[np.ndarray] | None,
    list[np.ndarray] | None,
]:
    """
    Parse a LuQY Pro data file that may contain single or multiple measurements.
    Returns per-measurement settings/results lists and spectral arrays.
    """
    # delimiter row
    delim_idx = None
    for idx, line in enumerate(lines):
        if re.match(r'^-[-\\s]*$', line.strip()):
            delim_idx = idx
            break
    if delim_idx is None:
        delim_idx = len(lines)

    header_lines = lines[:delim_idx]
    times: list[str] | None = None
    times_line_idx = -1

    # detect time row
    for i, line in enumerate(header_lines):
        stripped = line.strip()
        if not stripped:
            continue
        if '\t' in line:
            parts = line.split('\t')
            if len(parts) > 2 and (
                parts[0].strip().lower() == 'time' or '/' in parts[0]
            ):
                values = parts[1:] if parts[0].strip().lower() == 'time' else parts
                # "8/27/2025\t2:03 PM\t2:05 PM..."
                if '/' in values[0] and ':' not in values[0] and len(values) > 1:
                    date_prefix = values[0].strip()
                    times = []
                    for v in values[1:]:
                        v = v.strip()
                        if '/' in v and ':' in v:
                            times.append(v)
                        else:
                            times.append(f'{date_prefix} {v}')
                else:
                    times = [v.strip() for v in values if v.strip()]
                times_line_idx = i
                break
            if len(parts) == 2 and parts[0].strip().lower() == 'time':
                times = [parts[1].strip()]
                times_line_idx = i
                break
        else:
            # single measurement row without tabs
            parts_ws = re.split(r'\s+', stripped)
            if times is None and '/' in parts_ws[0]:
                times = [stripped]
                times_line_idx = i
                break

    if not times:
        times = []
        num_measurements = 1
    else:
        num_measurements = len(times)

    settings_vals_list: list[dict[str, object]] = [
        dict() for _ in range(num_measurements)
    ]
    result_vals_list: list[dict[str, float]] = [dict() for _ in range(num_measurements)]

    for idx, line in enumerate(header_lines):
        if not line.strip() or idx == times_line_idx:
            continue
        parts = line.split('\t') if '\t' in line else re.split(r'\s+', line.strip())
        if len(parts) < 2:
            continue
        key = _canon_key(parts[0])
        values = parts[1:]
        if num_measurements > 1 and len(values) >= num_measurements:
            for i in range(num_measurements):
                val_str = values[i].strip() if i < len(values) else ''
                if key in header_map_settings:
                    target = header_map_settings[key]
                    if target == 'subcell':
                        settings_vals_list[i][target] = val_str
                    else:
                        try:
                            v = float(val_str.replace(',', '.'))
                            if key == 'Laser intensity (suns)':
                                v *= 100.0  # 1 sun = 100 mW/cm²
                            settings_vals_list[i][target] = v
                        except ValueError:
                            if logger:
                                logger.debug(
                                    'Could not convert setting to float',
                                    key=key,
                                    value=val_str,
                                )
                elif key in header_map_result:
                    target = header_map_result[key]
                    try:
                        v = float(val_str.replace(',', '.'))
                        result_vals_list[i][target] = v
                    except ValueError:
                        if logger:
                            logger.debug(
                                'Could not convert result to float',
                                key=key,
                                value=val_str,
                            )
        else:
            val_str = values[0].strip()
            if key in header_map_settings:
                target = header_map_settings[key]
                if target == 'subcell':
                    settings_vals_list[0][target] = val_str
                else:
                    try:
                        v = float(val_str.replace(',', '.'))
                        if key == 'Laser intensity (suns)':
                            v *= 100.0
                        settings_vals_list[0][target] = v
                    except ValueError:
                        if logger:
                            logger.debug(
                                'Could not convert setting to float',
                                key=key,
                                value=val_str,
                            )
            elif key in header_map_result:
                target = header_map_result[key]
                try:
                    v = float(val_str.replace(',', '.'))
                    result_vals_list[0][target] = v
                except ValueError:
                    if logger:
                        logger.debug(
                            'Could not convert result to float', key=key, value=val_str
                        )

    if times:
        for i in range(num_measurements):
            settings_vals_list[i]['timestamp'] = times[i]

    # spectral parsing
    start_idx = delim_idx + 1
    while start_idx < len(lines) and not lines[start_idx].strip():
        start_idx += 1
    if start_idx < len(lines):
        start_idx += 1

    wavelengths: list[float] = []
    lum_lists: list[list[float]] = [[] for _ in range(num_measurements)]
    raw_lists: list[list[float]] | None = None
    dark_lists: list[list[float]] | None = None

    for line in lines[start_idx:]:
        stripped = line.strip()
        if not stripped:
            continue
        parts = line.split('\t') if '\t' in line else re.split(r'\s+', stripped)
        if len(parts) < 1 + num_measurements:
            continue
        try:
            wl = float(parts[0].replace(',', '.'))
        except ValueError:
            continue
        wavelengths.append(wl)
        values = parts[1:]
        channels = max(1, len(values) // num_measurements)
        idx_v = 0
        for i in range(num_measurements):
            try:
                lum = float(values[idx_v].replace(',', '.'))
            except ValueError:
                lum = float('nan')
            lum_lists[i].append(lum)
            idx_v += 1
            if channels >= 2:
                if raw_lists is None:
                    raw_lists = [[] for _ in range(num_measurements)]
                try:
                    raw = float(values[idx_v].replace(',', '.'))
                except (ValueError, IndexError):
                    raw = float('nan')
                raw_lists[i].append(raw)
                idx_v += 1
            if channels >= 3:
                if dark_lists is None:
                    dark_lists = [[] for _ in range(num_measurements)]
                try:
                    dark = float(values[idx_v].replace(',', '.'))
                except (ValueError, IndexError):
                    dark = float('nan')
                dark_lists[i].append(dark)
                idx_v += 1

    wavelength_arr = np.asarray(wavelengths, dtype=float)
    lum_arrays = [np.asarray(lst, dtype=float) for lst in lum_lists]
    raw_arrays = (
        [np.asarray(lst, dtype=float) for lst in raw_lists] if raw_lists else None
    )
    dark_arrays = (
        [np.asarray(lst, dtype=float) for lst in dark_lists] if dark_lists else None
    )

    return (
        settings_vals_list,
        result_vals_list,
        wavelength_arr,
        lum_arrays,
        raw_arrays,
        dark_arrays,
    )


def _parse_header(
    lines: list[str], logger: BoundLogger
) -> tuple[dict[str, float], dict[str, float], int]:
    """
    Parse the header of a LuQY Pro file.

    """
    header_map_settings = {
        'Time': 'timestamp',
        'Laser intensity (mW/cm^2)': 'laser_intensity',
        'Bias Voltage (V)': 'bias_voltage',
        'Bias voltage (V)': 'bias_voltage',
        'SMU current density (mA/cm^2)': 'smu_current_density',
        'Integration Time (ms)': 'integration_time',
        'Delay time (s)': 'delay_time',
        'EQE @ laser wavelength': 'eqe_at_laser',
        'Laser spot size (cm^2)': 'laser_spot_size',
        'Subcell area (cm^2)': 'subcell_area',
        'Subcell': 'subcell',
    }
    header_map_result = {
        'LuQY (%)': 'luqy',
        'QFLS (eV)': 'qfls',
        'QFLS LuQY (eV)': 'qfls',
        'QFLS HET (eV)': 'qfls_het',
        'QFLS Confidence': 'qfls_confidence',
        'QFLS confidence': 'qfls_confidence',
        'Bandgap (eV)': 'bandgap',
        'Jsc (mA/cm^2)': 'derived_jsc',
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
        key = _canon_key(key)
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
    Handles both single and multi‑measurement formats.
    """

    def __init__(self) -> None:
        super().__init__(name='luqy_pro_parser')
        self._mainfile_name_re = re.compile(FILE_RE)

    def is_mainfile(self, filename: str) -> bool | list[str]:
        """
        Detect multi‑measurement files: return a list of keys when multiple
        timestamps are present in the Time row, otherwise True.
        """
        basename = os.path.basename(filename)
        if not self._mainfile_name_re.match(basename):
            return False
        try:
            with open(filename, encoding='utf-8', errors='ignore') as f:
                lines = [f.readline().rstrip('\n') for _ in range(50) if f]
        except Exception:
            return True
        times = None
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) > 2 and (
                    parts[0].strip().lower() == 'time' or '/' in parts[0]
                ):
                    values = parts[1:] if parts[0].strip().lower() == 'time' else parts
                    if '/' in values[0] and ':' not in values[0] and len(values) > 1:
                        date_prefix = values[0].strip()
                        times = []
                        for v in values[1:]:
                            v = v.strip()
                            if '/' in v and ':' in v:
                                times.append(v)
                            else:
                                times.append(f'{date_prefix} {v}')
                    else:
                        times = [v.strip() for v in values if v.strip()]
                    break
                if len(parts) == 2 and parts[0].strip().lower() == 'time':
                    times = [parts[1].strip()]
                    break
        if times and len(times) > 1:
            return [str(i) for i in range(len(times))]
        return True

    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger: BoundLogger,
        child_archives: dict[str, EntryArchive] | None = None,
    ) -> None:
        # read bytes
        try:
            with archive.m_context.raw_file(mainfile, mode='rb') as f:
                raw_bytes = f.read()
        except Exception as e_ctx:
            logger.debug(
                'raw_file failed, falling back to open()',
                file=mainfile,
                error=str(e_ctx),
            )
            try:
                with open(mainfile, mode='rb') as f:
                    raw_bytes = f.read()
            except OSError as e:
                logger.error('Failed to open file ', file=mainfile, error=str(e))
                return
        try:
            text = raw_bytes.decode('utf-8', errors='strict')
        except UnicodeDecodeError:
            text = raw_bytes.decode('cp1252', errors='replace')
        text = text.replace('Â²', '²')

        lines = text.splitlines()
        if not lines:
            logger.warning('Empty LuQY file', file=mainfile)
            return

        # unified parsing for single/multi
        (
            settings_list,
            results_list,
            wavelengths,
            lum_arrays,
            raw_arrays,
            dark_arrays,
        ) = parse_multi(lines, logger=logger)

        measurements: list[LuQYProMeasurement] = []
        for i in range(len(settings_list)):
            meas = LuQYProMeasurement()
            meas.settings = LuQYProSettings()
            # settings
            for attr, val in settings_list[i].items():
                try:
                    setattr(meas.settings, attr, val)
                except Exception:
                    logger.debug('Unknown setting attribute', attr=attr)
            # results
            meas.results = [LuQYProResult()]
            r = meas.results[0]
            for attr, val in results_list[i].items():
                try:
                    setattr(r, attr, val)
                except Exception:
                    logger.debug('Unknown result attribute', attr=attr)
            # spectral arrays
            if wavelengths.size:
                try:
                    r.wavelength = wavelengths
                    r.luminescence_flux_density = lum_arrays[i]
                    if raw_arrays is not None:
                        r.raw_spectrum_counts = raw_arrays[i]
                    if dark_arrays is not None:
                        r.dark_spectrum_counts = dark_arrays[i]
                except Exception as e:
                    logger.debug('Error setting spectral arrays', error=str(e))
            measurements.append(meas)

        # distribute measurements
        if child_archives:
            for key in sorted(child_archives.keys(), key=lambda x: int(x)):
                idx = int(key)
                if idx < len(measurements):
                    child_archives[key].data = measurements[idx]
            # parent archive gets first measurement
            if measurements:
                archive.data = measurements[0]
        elif measurements:
            archive.data = measurements[0]
