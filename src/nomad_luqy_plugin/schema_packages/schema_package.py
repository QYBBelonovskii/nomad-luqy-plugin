from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    pass

import numpy as np
from nomad.config import config
from nomad.datamodel.data import Schema
from nomad.metainfo import Quantity, SchemaPackage

configuration = config.get_plugin_entry_point(
    'nomad_luqy_plugin.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage(name='luqy_schema')


class LuQYProMeasurement(Schema):
    times = Quantity(type=str, shape=['*'])
    luqy_percent = Quantity(type=np.float64, shape=['*'])
    qfls = Quantity(type=np.float64, shape=['*'], unit='eV')
    qfls_confidence = Quantity(type=np.float64, shape=['*'])
    laser_intensity = Quantity(type=np.float64, shape=['*'])
    bias_voltage = Quantity(type=np.float64, shape=['*'], unit='V')
    smu_current_density = Quantity(type=np.float64, shape=['*'], unit='mA/cm^2')
    integration_time = Quantity(type=np.float64, shape=['*'], unit='ms')
    delay_time = Quantity(type=np.float64, shape=['*'], unit='s')
    bandgap = Quantity(type=np.float64, shape=['*'], unit='eV')
    jsc = Quantity(type=np.float64, shape=['*'], unit='mA/cm^2')
    eqe_at_laser = Quantity(type=np.float64, shape=['*'])
    laser_spot_size = Quantity(type=np.float64, shape=['*'], unit='cm^2')
    subcell_area = Quantity(type=np.float64, shape=['*'], unit='cm^2')
    subcell = Quantity(type=str, shape=['*'])

    wavelength = Quantity(type=np.float64, shape=['*'], unit='nm')
    lum_flux_density = Quantity(
        type=np.float64, shape=['*', '*']
    )  # [n_wavelengths, n_times]


"""
class NewSchemaPackage(Schema):
    name = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )
    message = Quantity(type=str)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        logger.info('NewSchema.normalize', parameter=configuration.parameter)
        self.message = f'Hello {self.name}!'
"""

m_package.__init_metainfo__()
