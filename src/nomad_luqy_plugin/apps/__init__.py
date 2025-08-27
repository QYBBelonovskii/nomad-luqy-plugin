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
    name='LuQY Explorer',
    description='Explore LuQY Pro absolute PL measurements: filters, table and a demo dashboard.',
    app=App(
        label='LuQY',
        path='luqy',  # URL: /app/luqy
        category='Measurements',
        breadcrumb='Explore LuQY Pro',
        search_quantities=SearchQuantities(include=[f'*#{SCHEMA_QN}']),
        columns=Columns(
            selected=[
                'entry',
                'created',
                'luqy',
                'bandgap',
                'qfls',
                'jsc',
                'intensity',
                'spot',
                'area',
                'subcell',
            ],
            options={
                'entry': Column(quantity='entry_id', label='Entry', selected=False),
                'created': Column(
                    quantity='upload_create_time', label='Uploaded at', selected=True
                ),
                # SETTINGS
                'intensity': Column(
                    quantity=f'data.settings.laser_intensity_suns#{SCHEMA_QN}',
                    label='Laser intensity (suns)',
                    selected=True,
                ),
                'spot': Column(
                    quantity=f'data.settings.laser_spot_size#{SCHEMA_QN}',
                    label='Spot (cm²)',
                    unit='cm**2',
                    selected=True,
                ),
                'area': Column(
                    quantity=f'data.settings.subcell_area#{SCHEMA_QN}',
                    label='Area (cm²)',
                    unit='cm**2',
                    selected=True,
                ),
                'subcell': Column(
                    quantity=f'data.settings.subcell#{SCHEMA_QN}',
                    label='Subcell',
                    selected=True,
                ),
                # RESULTS
                'luqy': Column(
                    quantity=f'data.results[0].luminescence_quantum_yield#{SCHEMA_QN}',
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
                    quantity=f'data.results[0].quasi_fermi_level_splitting#{SCHEMA_QN}',
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
            },
        ),
        menu=Menu(
            title='Filters',
            size=MenuSizeEnum.MD,
            items=[
                MenuItemTerms(search_quantity='datasets.dataset_name', title='Dataset'),
                MenuItemTerms(
                    search_quantity=f'data.settings.subcell#{SCHEMA_QN}',
                    title='Subcell',
                ),
                MenuItemHistogram(
                    x=Axis(
                        search_quantity=f'data.settings.laser_intensity_suns#{SCHEMA_QN}'
                    ),
                    title='Laser intensity (suns)',
                    nbins=30,
                    show_input=True,
                ),
                MenuItemHistogram(
                    x=Axis(
                        search_quantity=f'data.results[*].luminescence_quantum_yield#{SCHEMA_QN}'
                    ),
                    title='LuQY (%)',
                    nbins=30,
                    show_input=True,
                ),
                MenuItemHistogram(
                    x=Axis(
                        search_quantity=f'data.results[*].bandgap#{SCHEMA_QN}',
                        unit='eV',
                    ),
                    title='Bandgap (eV)',
                    nbins=30,
                    show_input=True,
                ),
                MenuItemHistogram(
                    x=Axis(
                        search_quantity=f'data.results[*].quasi_fermi_level_splitting#{SCHEMA_QN}',
                        unit='eV',
                    ),
                    title='QFLS (eV)',
                    nbins=30,
                    show_input=True,
                ),
                MenuItemHistogram(
                    x=Axis(
                        search_quantity=f'data.results[*].derived_jsc#{SCHEMA_QN}',
                        unit='mA/cm**2',
                    ),
                    title='Jsc (mA/cm²)',
                    nbins=30,
                    show_input=True,
                ),
                MenuItemHistogram(
                    x=Axis(search_quantity='upload_create_time'),
                    title='Uploads over time',
                    nbins=30,
                    show_input=True,
                ),
            ],
        ),
        dashboard=Dashboard(
            widgets=[
                WidgetScatterPlot(
                    title='QFLS vs Bandgap',
                    x=Axis(
                        search_quantity=f'data.results[*].bandgap#{SCHEMA_QN}',
                        unit='eV',
                    ),
                    y=Axis(
                        search_quantity=f'data.results[*].quasi_fermi_level_splitting#{SCHEMA_QN}',
                        unit='eV',
                    ),
                    autorange=True,
                    layout={'lg': Layout(w=6, h=5, x=0, y=0)},
                ),
            ]
        ),
        filters_locked={'section_defs.definition_qualified_name': [SCHEMA_QN]},
    ),
)
