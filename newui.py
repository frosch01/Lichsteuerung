from nicegui import ui
from nicegui.events import ValueChangeEventArguments

def show(event: ValueChangeEventArguments):
    name = type(event.sender).__name__
    ui.notify(f'{name}: {event.value}')

with ui.grid(columns=2):
    with ui.card():
        ui.label("Lampe Einfahrt vorne").props('inline')
        ui.toggle({1: 'auto', 2: 'on', 3: 'off'}, value=1, on_change=show).props('inline')
        ui.icon('light_mode', color='yellow', size='32px').classes('text-5xl')
    with ui.card():
        ui.label("Lampe Einfahrt hinten").props('inline')
        ui.toggle({1: 'auto', 2: 'on', 3: 'off'}, value=1, on_change=show).props('inline')
        ui.icon('light_mode', color='gray', size='32px').classes('text-5xl')
    with ui.card():
        ui.label("Lampe Hof/Garten").props('inline')
        ui.toggle({1: 'auto', 2: 'on', 3: 'off'}, value=1, on_change=show).props('inline')
        ui.slider(min=0, max=100, value=100, on_change=show)
        ui.icon('light_mode', color='gray', size='32px').classes('text-5xl')
    with ui.card():
        ui.label("Lampe Garage").props('inline')
        ui.toggle({1: 'auto', 2: 'on', 3: 'off'}, value=1, on_change=show).props('inline')
        ui.icon('light_mode', color='gray', size='32px').classes('text-5xl')

    with ui.card():
        ui.label("Melder Einfahrt").props('inline')
        ui.toggle({1: 'active', 2: 'masked'}, value=1, on_change=show).props('inline')
    with ui.card():
        ui.label("Melder Hof/Garten").props('inline')
        ui.toggle({1: 'active', 2: 'masked'}, value=1, on_change=show).props('inline')
    with ui.card():
        ui.label("Melder Garage").props('inline')
        ui.toggle({1: 'active', 2: 'masked'}, value=1, on_change=show).props('inline')

with ui.card():
    columns = [
        {'name': 'meter', 'label': 'Zähler / kwh', 'field': 'meter', 'required': True, 'align': 'left'},
        {'name': 'day', 'label': 'Tag', 'field': 'day'},
        {'name': 'week', 'label': 'Woche', 'field': 'week'},
        {'name': 'month', 'label': 'Monat', 'field': 'month'},
        {'name': 'year', 'label': 'Jahr', 'field': 'year'},
    ]
    rows = [
        {'meter': 'Arbeiten + Schlafen', 'day': 3.25, 'week': 20.31, "month": 71.45, "year": 248.34},
        {'meter': 'Wohnen + Essen', 'day': 3.25, 'week': 20.31, "month": 71.45, "year": 248.34},
        {'meter': 'Mareike + Papa', 'day': 3.25, 'week': 20.31, "month": 71.45, "year": 248.34},
        {'meter': 'Licht', 'day': 0.25, 'week': 2.31, "month": 8.45, "year": 70.34},
    ]
    ui.table(columns=columns, rows=rows, row_key='name')

ui.run(binding_refresh_interval = 1, show = False)
