"""
Schema definitions for LuQY Pro absolute photoluminescence measurements.

This module defines a clean set of metainfo classes to represent the
metadata and results extracted from LuQY Pro files.

The measurement is split into a ``settings`` section (containing
experimental parameters) and a ``results`` section (containing both
scalar quantities and spectral arrays).  A top‑level measurement class
derives from ``Measurement`` and ``EntryData`` to ensure it can be used
as the root object of an archive entry.
"""

import numpy as np
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.datamodel.metainfo.basesections import (
    Measurement,
    MeasurementResult,
    ReadableIdentifiers,
)
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

m_package = SchemaPackage(name='luqy_pro_schema')


class LuQYProSettings(ArchiveSection):
    """
    Experimental parameters for a single LuQY Pro measurement.

    """

    m_def = Section(label='LuQYProSettings')

    laser_intensity_suns = Quantity(
        type=np.float64,
        description='Laser intensity in units of suns.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='Laser intensity (suns)',
        ),
    )
    bias_voltage = Quantity(
        type=np.float64,
        unit='V',
        description='Applied bias voltage during the measurement.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='Bias voltage',
        ),
    )
    smu_current_density = Quantity(
        type=np.float64,
        unit='mA/cm**2',
        description='Current density measured with the source‑meter unit.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='SMU current density',
        ),
    )
    integration_time = Quantity(
        type=np.float64,
        unit='ms',
        description='Integration time of the detector.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='Integration time',
        ),
    )
    delay_time = Quantity(
        type=np.float64,
        unit='s',
        description='Delay time after illumination before collection.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='Delay time',
        ),
    )
    eqe_at_laser = Quantity(
        type=np.float64,
        description='External quantum efficiency evaluated at the laser wavelength.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='EQE @ laser wavelength',
        ),
    )
    laser_spot_size = Quantity(
        type=np.float64,
        unit='cm**2',
        description='Area illuminated by the laser.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='Laser spot size',
        ),
    )
    subcell_area = Quantity(
        type=np.float64,
        unit='cm**2',
        description='Area of the subcell under investigation.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='Subcell area',
        ),
    )
    subcell = Quantity(
        type=str,
        description='Description or identifier of the subcell.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.RichTextEditQuantity,
            label='Subcell',
        ),
    )


class LuQYProResult(MeasurementResult):
    """
    Results of a single LuQY Pro measurement.
    Contains both scalar results and spectral data arrays.

    """

    m_def = Section(label='LuQYProResult')

    luminescence_quantum_yield = Quantity(
        type=np.float64,
        description='Luminescence quantum yield',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='LuQY (%)',
        ),
    )
    quasi_fermi_level_splitting = Quantity(
        type=np.float64,
        unit='eV',
        description='Quasi‑Fermi level splitting derived from the measurement.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='iVoc (eV)',
        ),
    )
    qfls_confidence = Quantity(
        type=np.float64,
        description='Quasi-Fermi level splitting.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='iVoc confidence',
        ),
    )
    bandgap = Quantity(
        type=np.float64,
        unit='eV',
        description='Bandgap of the material.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='Bandgap (eV)',
        ),
    )
    derived_jsc = Quantity(
        type=np.float64,
        unit='mA/cm**2',
        description='Short‑circuit current density derived from the measurement.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='Jsc (mA/cm²)',
        ),
    )

    wavelength = Quantity(
        type=np.float64,
        unit='nm',
        shape=['*'],
        description='Wavelength axis of the measured spectrum.',
    )
    luminescence_flux_density = Quantity(
        type=np.float64,
        unit='s/(cm**2*nm)',
        shape=['*'],
        description='Spectral luminescence flux density (photons/(s cm² nm)).',
    )
    raw_spectrum_counts = Quantity(
        type=np.float64,
        shape=['*'],
        description='Raw detector counts as reported by the instrument.',
    )
    dark_spectrum_counts = Quantity(
        type=np.float64,
        shape=['*'],
        description='Detector counts collected with the shutter closed.',
    )


class LuQYProMeasurement(Measurement, EntryData):
    """
    Top level class representing a LuQY Pro measurement entry.

    Combines settings and results into a single entity.
    By inheriting from ``EntryData``, an instance can be assigned as ``archive.data``.

    """

    method = Quantity(
        type=str,
        default='LuQY Pro absolute photoluminescence',
        description='Descriptive name of the measurement method.',
    )

    settings: LuQYProSettings = SubSection(
        section_def=LuQYProSettings,
        description='Experimental parameters used for the measurement.',
    )

    results = Measurement.results.m_copy()
    results.section_def = LuQYProResult

    measurement_identifiers = SubSection(
        section_def=ReadableIdentifiers,
        description='Optional identifiers such as sample ID, operator or instrument.',
    )

    m_def = Section(label='LuQY Pro measurement')


m_package.__init_metainfo__()
