from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Column,
    Columns,
    Menu,
    MenuItemTerms,
    MenuSizeEnum,
    SearchQuantities,
)

SCHEMA_QN = 'nomad_luqy_plugin.schema_packages.schema_package.LuQYProMeasurement'

app_entry_point = AppEntryPoint(
    name='LuQY Pro',
    description='Browse LuQY Pro entries (minimal safe app).',
    app=App(
        label='LuQY Pro',
        path='luqypro',  # <= ровно сюда ты заходишь
        category='Measurements',
        breadcrumb='Explore LuQY Pro',
        search_quantities=SearchQuantities(include=[f'*#{SCHEMA_QN}']),
        columns=Columns(
            selected=['entry', 'luqy', 'bandgap', 'qfls'],
            options={
                'entry': Column(
                    quantity='entry_id',
                    label='Entry',
                    selected=True,
                ),
                'luqy': Column(
                    quantity=(
                        f'data.results[0].luminescence_quantum_yield#{SCHEMA_QN}'
                    ),
                    label='LuQY (%)',
                    selected=True,
                ),
                'bandgap': Column(
                    quantity=f'data.results[0].bandgap#{SCHEMA_QN}',
                    label='Bandgap (eV)',
                    unit='eV',
                    selected=True,
                ),
                'qfls': Column(
                    quantity=(
                        f'data.results[0].quasi_fermi_level_splitting#{SCHEMA_QN}'
                    ),
                    label='QFLS (eV)',
                    unit='eV',
                    selected=True,
                ),
            },
        ),
        # Без гистограмм и дашборда, только безопасный terms-фильтр
        menu=Menu(
            title='Filters',
            size=MenuSizeEnum.SM,
            items=[
                MenuItemTerms(
                    search_quantity=f'data.settings.subcell#{SCHEMA_QN}',
                    title='Subcell',
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
