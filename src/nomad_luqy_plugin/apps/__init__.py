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
    name='LuQY Pro',
    description='Browse LuQY Pro entries: filters, table, and a demo scatter.',
    app=App(
        label='LuQY Pro',
        path='luqypro',
        category='Measurements',
        breadcrumb='Explore LuQY Pro',
        search_quantities=SearchQuantities(include=[f'*#{SCHEMA_QN}']),
        columns=Columns(
            selected=['created', 'luqy', 'bandgap', 'qfls', 'jsc'],
            options={
                'created': Column(
                    quantity='upload_create_time',
                    label='Uploaded at',
                    selected=True,
                ),
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
            },
        ),
        menu=Menu(
            title='Filters',
            size=MenuSizeEnum.MD,
            items=[
                # Останется терминами (категории) – безопасно
                MenuItemTerms(
                    search_quantity=f'data.settings.subcell#{SCHEMA_QN}',
                    title='Subcell',
                ),
                # Только числовые скаляры без [*]
                MenuItemHistogram(
                    x=Axis(
                        search_quantity=(
                            f'data.settings.laser_intensity_suns#{SCHEMA_QN}'
                        )
                    ),
                    title='Laser intensity (suns)',
                    nbins=30,
                    show_input=True,
                ),
                MenuItemHistogram(
                    x=Axis(
                        search_quantity=(
                            f'data.results[0].luminescence_quantum_yield#{SCHEMA_QN}'
                        )
                    ),
                    title='LuQY (%)',
                    nbins=30,
                    show_input=True,
                ),
            ],
        ),
        dashboard=Dashboard(
            widgets=[
                WidgetScatterPlot(
                    title='QFLS vs Bandgap (first result)',
                    x=Axis(
                        search_quantity=f'data.results[0].bandgap#{SCHEMA_QN}',
                        unit='eV',
                    ),
                    y=Axis(
                        search_quantity=(
                            f'data.results[0].quasi_fermi_level_splitting#{SCHEMA_QN}'
                        ),
                        unit='eV',
                    ),
                    autorange=True,
                    layout={'lg': Layout(w=6, h=5, x=0, y=0)},
                ),
            ]
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
