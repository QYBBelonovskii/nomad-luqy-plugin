from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Axis,
    Column,
    Columns,
    Dashboard,
    Layout,
    Menu,
    MenuItemHistogram,
    MenuItemTerms,
    MenuSizeEnum,
    SearchQuantities,
    WidgetScatterPlot,
)

SCHEMA_QN = 'nomad_luqy_plugin.schema_packages.schema_package.LuQYProMeasurement'

app_entry_point = AppEntryPoint(
    name='LuQY Pro Explorer',
    description=(
        'Browse and analyze LuQY Pro absolute PL measurements: '
        'datasets, table, filters and quick charts.'
    ),
    app=App(
        label='LuQY Pro',
        path='luqypro',
        category='Measurements',
        breadcrumb='Explore LuQY Pro',
        search_quantities=SearchQuantities(include=[f'*#{SCHEMA_QN}']),
        columns=Columns(
            selected=[
                'mainfile',
                'created',
                'luqy',
                'bandgap',
                'qfls',
                'jsc',
                'intensity',
                'tint',
                'delay',
                'spot',
                'area',
                'subcell',
            ],
            options={
                'mainfile': Column(
                    quantity='mainfile',
                    label='File',
                    selected=True,
                ),
                'created': Column(
                    quantity='upload_create_time',
                    label='Uploaded at',
                    selected=True,
                ),
                'dataset': Column(
                    quantity='datasets.dataset_name',
                    label='Dataset',
                    selected=False,
                ),
                # RESULTS
                'luqy': Column(
                    quantity=(
                        f'data.results[0].luminescence_quantum_yield#{SCHEMA_QN}'
                    ),
                    label='LuQY (%)',
                    selected=True,
                    format={'decimals': 4, 'mode': 'standard'},
                ),
                'bandgap': Column(
                    quantity=f'data.results[0].bandgap#{SCHEMA_QN}',
                    label='Bandgap (eV)',
                    unit='eV',
                    selected=True,
                    format={'decimals': 3, 'mode': 'standard'},
                ),
                'qfls': Column(
                    quantity=(
                        f'data.results[0].quasi_fermi_level_splitting#{SCHEMA_QN}'
                    ),
                    label='QFLS (eV)',
                    unit='eV',
                    selected=True,
                    format={'decimals': 3, 'mode': 'standard'},
                ),
                'jsc': Column(
                    quantity=f'data.results[0].derived_jsc#{SCHEMA_QN}',
                    label='Jsc (mA/cm²)',
                    unit='mA/cm**2',
                    selected=True,
                    format={'decimals': 3, 'mode': 'standard'},
                ),
                # SETTINGS
                'intensity': Column(
                    quantity=(f'data.settings.laser_intensity_suns#{SCHEMA_QN}'),
                    label='Laser suns',
                    selected=True,
                    format={'decimals': 3, 'mode': 'standard'},
                ),
                'tint': Column(
                    quantity=(f'data.settings.integration_time#{SCHEMA_QN}'),
                    label='Integration (ms)',
                    unit='ms',
                    selected=True,
                    format={'decimals': 2, 'mode': 'standard'},
                ),
                'delay': Column(
                    quantity=f'data.settings.delay_time#{SCHEMA_QN}',
                    label='Delay (s)',
                    unit='s',
                    selected=True,
                    format={'decimals': 2, 'mode': 'standard'},
                ),
                'spot': Column(
                    quantity=f'data.settings.laser_spot_size#{SCHEMA_QN}',
                    label='Spot (cm²)',
                    unit='cm**2',
                    selected=True,
                    format={'decimals': 3, 'mode': 'standard'},
                ),
                'area': Column(
                    quantity=f'data.settings.subcell_area#{SCHEMA_QN}',
                    label='Area (cm²)',
                    unit='cm**2',
                    selected=True,
                    format={'decimals': 3, 'mode': 'standard'},
                ),
                'subcell': Column(
                    quantity=f'data.settings.subcell#{SCHEMA_QN}',
                    label='Subcell',
                    selected=True,
                ),
            },
        ),
        # LEFT FILTERS
        menu=Menu(
            title='Filters',
            size=MenuSizeEnum.MD,
            items=[
                # Categorical filters
                MenuItemTerms(
                    search_quantity='datasets.dataset_name',
                    title='Dataset',
                ),
            ],
        ),
    ),
)


"""
from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import App, Column, Columns, FilterMenu, FilterMenus

app_entry_point = AppEntryPoint(
    name='NewApp',
    description='New app entry point configuration.',
    app=App(
        label='NewApp',
        path='app',
        category='simulation',
        columns=Columns(
            selected=['entry_id'],
            options={
                'entry_id': Column(),
            },
        ),
        filter_menus=FilterMenus(
            options={
                'material': FilterMenu(label='Material'),
            }
        ),
    ),
)
"""
