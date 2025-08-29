from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Axis,
    Column,
    Dashboard,
    Layout,
    Menu,
    MenuItemHistogram,
    MenuItemTerms,
    SearchQuantities,
    WidgetScatterPlot,
)

SCHEMA_QN = 'nomad_luqy_plugin.schema_packages.schema_package.LuQYProMeasurement'

app_entry_point = AppEntryPoint(
    name='LuQY Pro Explorer',
    description=('Browse and analyze LuQY Pro absolute PL measurements.'),
    app=App(
        label='LuQY Pro',
        path='luqypro',
        category='Measurements',
        breadcrumb='Explore LuQY Pro',
        search_quantities=SearchQuantities(include=[f'*#{SCHEMA_QN}']),
        filters_locked={'section_defs.definition_qualified_name': [SCHEMA_QN]},
        columns=[
            Column(quantity='mainfile', label='File', selected=True),
            Column(quantity='upload_create_time', label='Uploaded at', selected=True),
            # Results
            Column(
                quantity=f'data.results[0].luqy#{SCHEMA_QN}',
                label='LuQY (%)',
                selected=True,
                format={'decimals': 4, 'mode': 'standard'},
            ),
            Column(
                quantity=f'data.results[0].bandgap#{SCHEMA_QN}',
                label='Bandgap',
                unit='eV',
                selected=True,
                format={'decimals': 3, 'mode': 'standard'},
            ),
            Column(
                quantity=f'data.results[0].qfls#{SCHEMA_QN}',
                label='QFLS',
                unit='eV',
                selected=True,
                format={'decimals': 3, 'mode': 'standard'},
            ),
            Column(
                quantity=f'data.results[0].derived_jsc#{SCHEMA_QN}',
                label='Jsc',
                unit='mA/cm**2',
                selected=True,
                format={'decimals': 3, 'mode': 'standard'},
            ),
            # Settings
            Column(
                quantity=f'data.settings.laser_intensity#{SCHEMA_QN}',
                label='Laser',
                unit='mW/cm**2',
                selected=True,
                format={'decimals': 2, 'mode': 'standard'},
            ),
            Column(
                quantity=f'data.settings.integration_time#{SCHEMA_QN}',
                label='Integration',
                unit='ms',
                selected=True,
                format={'decimals': 0, 'mode': 'standard'},
            ),
            Column(
                quantity=f'data.settings.delay_time#{SCHEMA_QN}',
                label='Delay',
                unit='s',
                selected=False,
            ),
            Column(
                quantity=f'data.settings.laser_spot_size#{SCHEMA_QN}',
                label='Spot',
                unit='cm**2',
                selected=False,
            ),
            Column(
                quantity=f'data.settings.subcell_area#{SCHEMA_QN}',
                label='Area',
                unit='cm**2',
                selected=False,
            ),
            Column(
                quantity=f'data.settings.subcell#{SCHEMA_QN}',
                label='Subcell',
                selected=False,
            ),
            Column(
                quantity=f'data.settings.timestamp#{SCHEMA_QN}',
                label='Measured at',
                selected=False,
            ),
            Column(
                quantity='datasets.dataset_name',
                label='Dataset',
                selected=False,
            ),
        ],
        # LEFT FILTERS
        menu=Menu(
            title='Filters',
            items=[
                MenuItemTerms(
                    title='Dataset',
                    quantity='datasets.dataset_name',
                ),
            ],
        ),
        # data visualization  charts
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
