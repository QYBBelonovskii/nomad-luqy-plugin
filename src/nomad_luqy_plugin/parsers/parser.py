"""
Parser implementation for LuQY Pro absolute photoluminescence files.

"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime
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
        .replace('mW/cm2', 'mW/cm^2')
        .replace('mW/cm²', 'mW/cm^2')
    )
    s = re.sub(r'\s+', ' ', s)
    return s


def _to_iso8601(ts: str) -> str:
    ts = ts.strip()
    # LuQY Pro formats: 'M/D/YYYY h:mm:ss AM/PM' or 24h
    fmts = ('%m/%d/%Y %I:%M:%S %p', '%m/%d/%Y %H:%M:%S')
    for fmt in fmts:
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.strftime('%Y-%m-%dT%H:%M:%S')
        except ValueError:
            pass
    # try ISO
    try:
        # Python 3.11+: fromisoformat supports 'YYYY-MM-DDTHH:MM:SS'
        dt = datetime.fromisoformat(ts.replace(' ', 'T'))
        return dt.strftime('%Y-%m-%dT%H:%M:%S')
    except Exception:
        return ts  # fallback: keep as-is (better than losing it)


_HEADER_MAP_SETTINGS: dict[str, str] = {
    'Laser intensity (mW/cm^2)': 'laser_intensity',
    'Laser intensity (suns)': 'laser_intensity',
    'Bias Voltage (V)': 'bias_voltage',
    'Bias voltage (V)': 'bias_voltage',
    'SMU current density (mA/cm^2)': 'smu_current_density',
    'Integration Time (ms)': 'integration_time',
    'Delay time (s)': 'delay_time',
    'Delay Time (s)': 'delay_time',
    'EQE @ laser wavelength': 'eqe_at_laser',
    'Laser spot size (cm^2)': 'laser_spot_size',
    'Subcell area (cm^2)': 'subcell_area',
    'Subcell': 'subcell',
}

_HEADER_MAP_RESULTS: dict[str, str] = {
    'LuQY (%)': 'luqy',
    'QFLS (eV)': 'qfls',
    'QFLS LuQY (eV)': 'qfls',
    'QFLS HET (eV)': 'qfls_het',
    'QFLS Confidence': 'qfls_confidence',
    'QFLS confidence': 'qfls_confidence',
    'Bandgap (eV)': 'bandgap',
    'Jsc (mA/cm^2)': 'derived_jsc',
}


def _parse_settings_as_lists(
    lines: list[str], logger: BoundLogger
) -> tuple[dict[str, list[object]], int]:
    """ """
    data_start_idx: int = len(lines)
    for idx, line in enumerate(lines):
        if re.match(r'^-[-\\s]*$', line.strip()):
            data_start_idx = idx + 2
            break
    header_end = data_start_idx - 2 if data_start_idx < len(lines) else len(lines)
    header_lines = lines[:header_end]

    # 0)
    times: list[str] = []
    for line in header_lines:
        if '\t' not in line:
            continue
        parts = line.rstrip('\n').split('\t')
        if not parts:
            continue
        first_raw = parts[0].strip()
        first = _canon_key(first_raw).lower()
        if first == 'time':
            values = [v.strip() for v in parts[1:] if v.strip()]
            times = [_to_iso8601(v) for v in values] if values else []
            break
        # old style: first cell looks like a date (contains '/'), then times follow
        if '/' in first_raw and len(parts) > 1:
            date_prefix = first_raw.strip()
            values = [v.strip() for v in parts[1:] if v.strip()]
            if values:
                times = [_to_iso8601(f'{date_prefix} {v}') for v in values]
                break
    # 1)
    num_meas = 1
    for line in header_lines:
        if '\t' not in line:
            continue
        parts = line.rstrip('\n').split('\t')
        if not parts:
            continue
        key = _canon_key(parts[0])
        if key in _HEADER_MAP_SETTINGS:
            n_here = sum(1 for v in parts[1:] if v.strip())
            num_meas = max(num_meas, n_here)

    # 2)
    settings_cols: dict[str, list[object]] = {}
    for k, target in _HEADER_MAP_SETTINGS.items():
        if target == 'subcell':
            settings_cols[target] = [''] * num_meas
        else:
            settings_cols[target] = [np.nan] * num_meas

    # 3)
    for line in header_lines:
        if '\t' not in line:
            continue
        parts = line.rstrip('\n').split('\t')
        if not parts or len(parts) < 2:
            continue
        key = _canon_key(parts[0])
        if key not in _HEADER_MAP_SETTINGS:
            continue
        target = _HEADER_MAP_SETTINGS[key]
        values = parts[1:]
        for i in range(num_meas):
            val_str = values[i].strip() if i < len(values) else ''
            if target == 'subcell':
                settings_cols[target][i] = val_str
            else:
                if not val_str:
                    continue
                try:
                    v = float(val_str.replace(',', '.'))
                    # convert suns → mW/cm^2 on the fly
                    if target == 'laser_intensity' and key == 'Laser intensity (suns)':
                        v *= 100.0
                    settings_cols[target][i] = v
                except Exception:
                    logger.debug(
                        'Could not convert setting to float', key=key, value=val_str
                    )
    if times:
        ts = times + [''] * (num_meas - len(times))
        settings_cols['timestamp'] = ts[:num_meas]

    return settings_cols, data_start_idx


def _parse_results_as_lists(
    lines: list[str],
    logger: BoundLogger,
    num_meas_hint: int,
) -> dict[str, list[float]]:
    """
    Parse results header rows into dict[target, list[float]] of length num_meas.
    - LuQY (%)
    - QFLS/QFLS HET/Bandgap in eV -> float
    - QFLS Confidence -> float
    - Jsc (mA/cm^2) -> float
    """
    # find header end (same logic as settings)
    data_start_idx: int = len(lines)
    for idx, line in enumerate(lines):
        if re.match(r'^-[-\\s]*$', line.strip()):
            data_start_idx = idx + 2
            break
    header_end = data_start_idx - 2 if data_start_idx < len(lines) else len(lines)
    header_lines = lines[:header_end]

    # determine number of measurements based on results rows too
    num_meas = max(1, num_meas_hint)
    for line in header_lines:
        if '\t' not in line:
            continue
        parts = line.rstrip('\n').split('\t')
        if not parts:
            continue
        key = _canon_key(parts[0])
        if key in _HEADER_MAP_RESULTS:
            n_here = sum(1 for v in parts[1:] if v.strip())
            num_meas = max(num_meas, n_here)

    # init results columns
    results_cols: dict[str, list[float]] = {}
    targets = set(_HEADER_MAP_RESULTS.values())
    for t in targets:
        results_cols[t] = [np.nan] * num_meas

    # fill values
    for line in header_lines:
        if '\t' not in line:
            continue
        parts = line.rstrip('\n').split('\t')
        if not parts or len(parts) < 2:
            continue
        key = _canon_key(parts[0])
        if key not in _HEADER_MAP_RESULTS:
            continue
        target = _HEADER_MAP_RESULTS[key]
        values = parts[1:]
        for i in range(num_meas):
            val_str = values[i].strip() if i < len(values) else ''
            if not val_str:
                continue
            try:
                v = float(val_str.replace(',', '.'))
                results_cols[target][i] = v
            except Exception:
                logger.debug(
                    'Could not convert result to float', key=key, value=val_str
                )

    return results_cols


def _parse_spectra_multi(
    lines: list[str],
    data_start_idx: int,
    num_meas: int,
    logger: BoundLogger,
) -> tuple[
    np.ndarray, list[np.ndarray], list[np.ndarray] | None, list[np.ndarray] | None
]:
    """
    Parse spectral data after the '----' delimiter.

    Rules:
    - MULTI: rows look like: Wavelength  Lum(m1)  Lum(m2) ... Lum(mN)
            -> we return wavelength + list of N lum arrays
    - SINGLE (fallback): rows may be 4 columns: Wavelength  Lum  Raw  Dark
            -> we return wavelength + [lum] and raw/dark arrays for the single measurement

    Returns:
        wavelength: np.ndarray
        lum_lists: list[np.ndarray] length = num_meas
        raw_lists: list[np.ndarray] | None  (only for single with 4 columns)
        dark_lists: list[np.ndarray] | None (only for single with 4 columns)
    """
    # find first data row (skip blank lines) and skip the spectral header line
    i = data_start_idx
    while i < len(lines) and not lines[i].strip():
        i += 1
    # skip header row like 'Wavelength (nm)\t...'
    if i < len(lines):
        i += 1

    wavelengths: list[float] = []
    lum_lists: list[list[float]] = [[] for _ in range(max(1, num_meas))]
    raw_lists: list[list[float]] | None = None
    dark_lists: list[list[float]] | None = None

    for line in lines[i:]:
        s = line.strip()
        if not s:
            continue
        parts = s.split('\t') if '\t' in s else re.split(r'\s+', s)
        if len(parts) < 2:
            continue
        # wavelength
        try:
            wl = float(parts[0].replace(',', '.'))
        except ValueError:
            # not a data row
            continue
        wavelengths.append(wl)
        values = parts[1:]

        if num_meas > 1:
            # MULTI: expect at least 1 value per measurement (lum only)
            if len(values) < num_meas:
                # malformed row, pad with NaNs
                values = values + [''] * (num_meas - len(values))
            for j in range(num_meas):
                try:
                    lum = (
                        float(values[j].replace(',', '.'))
                        if values[j]
                        else float('nan')
                    )
                except ValueError:
                    lum = float('nan')
                lum_lists[j].append(lum)
            # by design: no raw/dark for multi (ignored even if present)
        else:
            # SINGLE: support 2 or 4 columns
            # 2 cols -> wavelength + lum
            # 4 cols -> wavelength + lum + raw + dark
            try:
                lum = float(values[0].replace(',', '.')) if values[0:] else float('nan')
            except ValueError:
                lum = float('nan')
            lum_lists[0].append(lum)

            if len(values) >= 3:
                if raw_lists is None:
                    raw_lists = [[]]
                    dark_lists = [[]]
                try:
                    raw = float(values[1].replace(',', '.'))
                except (ValueError, IndexError):
                    raw = float('nan')
                try:
                    dark = float(values[2].replace(',', '.'))
                except (ValueError, IndexError):
                    dark = float('nan')
                raw_lists[0].append(raw)
                dark_lists[0].append(dark)

    wavelength_arr = np.asarray(wavelengths, dtype=float)
    lum_arrays = [np.asarray(v, dtype=float) for v in lum_lists]
    raw_arrays = (
        [np.asarray(v, dtype=float) for v in raw_lists]
        if raw_lists is not None
        else None
    )
    dark_arrays = (
        [np.asarray(v, dtype=float) for v in dark_lists]
        if dark_lists is not None
        else None
    )
    return wavelength_arr, lum_arrays, raw_arrays, dark_arrays


class LuQYParser(MatchingParser):
    """
    Parser for LuQY Pro files.
    Matches files with extensions .txt, .csv, .tsv.
    Parses settings, results, and spectral data.

    """

    def __init__(self) -> None:
        super().__init__(name='luqy_pro_parser')
        self._mainfile_name_re = re.compile(FILE_RE)

    def is_mainfile(
        self,
        filename: str,
        mime: str | None = None,
        buffer: bytes | None = None,
        decoded_buffer: str | None = None,
        compression: str | None = None,
    ):
        if not self._mainfile_name_re.match(filename):
            return False

        try:
            with open(filename, encoding='utf-8', errors='ignore') as f:
                first_line = f.readline()
        except Exception:
            return ['0']

        parts = first_line.strip().split('\t')
        n = sum(1 for v in parts[1:] if v.strip()) if len(parts) > 1 else 0
        n = max(n, 1)

        return [str(i) for i in range(n)]

    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger: BoundLogger,
        child_archives: dict[str, EntryArchive] | None = None,
    ) -> None:
        logger.debug('Parsing LuQY Pro file', file=mainfile)
        logger.debug('Child child_archives', child_archives=child_archives)
        logger.debug('Archive before parsing', archive=archive)

        # read file content (try archive context first, then fallback to open)
        raw_bytes: bytes

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
                logger.error('Failed to open file', file=mainfile, error=str(e))
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

        settings_cols, data_start_idx = _parse_settings_as_lists(lines, logger)
        num_meas = max(len(v) for v in settings_cols.values()) if settings_cols else 1

        results_cols = _parse_results_as_lists(lines, logger, num_meas_hint=num_meas)

        wavelength_arr, lum_arrays, raw_arrays, dark_arrays = _parse_spectra_multi(
            lines, data_start_idx, num_meas, logger
        )

        def build_measurement(idx: int) -> LuQYProMeasurement:
            meas = LuQYProMeasurement()
            meas.settings = LuQYProSettings()
            for attr, lst in settings_cols.items():
                val = (
                    lst[idx]
                    if idx < len(lst)
                    else ('' if attr in ('subcell', 'timestamp') else np.nan)
                )
                try:
                    setattr(meas.settings, attr, val)
                except Exception:
                    logger.debug('Unknown setting attribute', attr=attr)

            r = LuQYProResult()
            for attr, lst in results_cols.items():
                val = lst[idx] if idx < len(lst) else np.nan
                try:
                    if isinstance(val, float) and np.isnan(val):
                        continue
                    setattr(r, attr, val)
                except Exception:
                    logger.debug('Unknown result attribute', attr=attr)
            meas.results = [r]

            try:
                if wavelength_arr.size:
                    # common wavelength for all measurements
                    # lum for current measurement
                    # raw/dark only present for single-measurement files with 4 columns
                    # (lum_arrays[idx] always exists; raw/dark may be None)
                    if not hasattr(meas, 'results') or not meas.results:
                        # ensure there is at least one result object
                        meas.results = [LuQYProResult()]
                    r = meas.results[0]
                    r.wavelength = wavelength_arr
                    r.luminescence_flux_density = (
                        lum_arrays[idx]
                        if idx < len(lum_arrays)
                        else np.array([], dtype=float)
                    )
                    if (
                        raw_arrays is not None
                        and len(raw_arrays) > 0
                        and idx < len(raw_arrays)
                    ):
                        r.raw_spectrum_counts = raw_arrays[idx]
                    if (
                        dark_arrays is not None
                        and len(dark_arrays) > 0
                        and idx < len(dark_arrays)
                    ):
                        r.dark_spectrum_counts = dark_arrays[idx]
            except Exception as e:
                logger.debug('Error setting spectral arrays', error=str(e))

            return meas

        if child_archives:
            # multi:
            for key, ch in child_archives.items():
                i = int(key)
                ch.data = build_measurement(i)
            return

        # single:
        archive.data = build_measurement(0)
