from __future__ import annotations

import re
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config
from nomad.parsing.parser import MatchingParser

configuration = config.get_plugin_entry_point(
    'nomad_luqy_plugin.parsers:parser_entry_point'
)

FILE_RE = r'.*\.(?:txt|csv|tsv)$'


class LuQYParser(MatchingParser):
    def __init__(self):
        super().__init__(name='luqy_parser')
        self._mainfile_name_re = re.compile(FILE_RE)

    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger: BoundLogger,
        child_archives: dict[str, EntryArchive] | None = None,
    ) -> None:
        from nomad_luqy_plugin.schema_packages.schema_package import LuQYProMeasurement

        with open(mainfile, encoding='utf-8', errors='ignore') as f:
            lines = [ln.rstrip('\n') for ln in f]

        if not lines:
            logger.warning('LuQYParser.parse', msg='empty file')
            return

        sep_regex = r'\t+|\s{2,}'

        times = [p for p in re.split(sep_regex, lines[0].strip()) if p]
        n_times = len(times)

        cut = None
        for i, ln in enumerate(lines[1:], start=1):
            if ln.strip().startswith('---'):
                cut = i
                break
        if cut is None:
            for i, ln in enumerate(lines[1:], start=1):
                if ln.strip().lower().startswith('wavelength'):
                    cut = i - 1
                    break

        param_lines = lines[1:cut] if cut else lines[1:]
        spectrum_start = None
        if cut is not None:
            j = cut + 1

            while j < len(lines) and not re.match(r'^\s*\d', lines[j]):
                j += 1
            spectrum_start = j if j < len(lines) else None

        def split_row(s: str) -> list[str]:
            return [p for p in re.split(sep_regex, s.strip()) if p != '']

        params: dict[str, list[float]] = {}
        for ln in param_lines:
            s = ln.strip()
            if not s or s.startswith('-'):
                continue
            parts = split_row(ln)
            if len(parts) < 2:
                continue
            name = parts[0].strip()
            vals = parts[1 : 1 + n_times]

            out = []
            for v in vals:
                try:
                    out.append(float(v.replace(',', '.')))
                except Exception:
                    out.append(np.nan)

            if len(out) < n_times:
                out += [np.nan] * (n_times - len(out))
            params[name] = out

        wavelength = []
        spectra_rows = []
        if spectrum_start is not None:
            for ln in lines[spectrum_start:]:
                if not ln.strip():
                    continue
                parts = split_row(ln)
                if not parts or not re.match(r'^\d', parts[0]):
                    continue
                try:
                    wl = float(parts[0].replace(',', '.'))
                except Exception:
                    continue
                vals = []
                for v in parts[1 : 1 + n_times]:
                    try:
                        vals.append(float(v.replace(',', '.')))
                    except Exception:
                        vals.append(np.nan)
                if len(vals) < n_times:
                    vals += [np.nan] * (n_times - len(vals))
                wavelength.append(wl)
                spectra_rows.append(vals)

        wavelength = np.array(wavelength, dtype=float)
        lum_flux_density = (
            np.array(spectra_rows, dtype=float)
            if spectra_rows
            else np.zeros((0, 0), dtype=float)
        )

        meas = LuQYProMeasurement()
        meas.times = times

        meas.luqy_percent = params.get('LuQY (%)')
        meas.qfls = params.get('QFLS (eV)')
        meas.qfls_confidence = params.get('QFLS confidence')
        meas.laser_intensity = params.get('Laser intensity (suns)')
        meas.bias_voltage = params.get('Bias voltage (V)')
        meas.smu_current_density = params.get(
            'SMU current density (mA/cm2)'
        ) or params.get('SMU current density (mA/cm^2)')
        meas.integration_time = params.get('Integration Time (ms)')
        meas.delay_time = params.get('Delay time (s)')
        meas.bandgap = params.get('Bandgap (eV)')
        meas.jsc = params.get('Jsc (mA/cm2)') or params.get('Jsc (mA/cm^2)')
        meas.eqe_at_laser = params.get('EQE @ laser wavelength')
        meas.laser_spot_size = params.get('Laser spot size (cm )') or params.get(
            'Laser spot size (cm^2)'
        )
        meas.subcell_area = params.get('Subcell area (cm )') or params.get(
            'Subcell area (cm^2)'
        )
        meas.subcell = params.get('Subcell')

        meas.wavelength = wavelength
        if lum_flux_density.size > 0:
            meas.lum_flux_density = lum_flux_density

        archive.data = meas


"""
class NewParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        logger.info('NewParser.parse', parameter=configuration.parameter)

        archive.workflow2 = Workflow(name='test')

"""
