import asyncio
from nicegui import app, ui
from nicegui.events import ValueChangeEventArguments
from light_control_new import LightControl
from sun import SunEvent, SunEventType

light_control = LightControl()

with ui.tabs() as tabs:
    light = ui.tab('Licht')
    detector = ui.tab('Melder')
    energy = ui.tab('Energie')
with ui.tab_panels(tabs, value=light):
    with ui.tab_panel(light).classes('p-1 m-0 gap-1'):
        #with ui.grid(columns=2):
        with ui.card():
            ui.label("Lampe Einfahrt vorne").props('inline')
            with ui.row():
                ui_lamp_yard_front_state = ui.icon('light_mode', color='gray', size='32px').classes('text-5xl')
                ui_lamp_yard_front_mode = ui.toggle({1: 'auto', 2: 'on', 3: 'off'}, value=1, on_change=lambda e: light_control.set_relais_mode('yard_front', e.value)).props('inline')
        with ui.card():
            ui.label("Lampe Einfahrt hinten").props('inline')
            with ui.row():
                ui_lamp_yard_rear_state = ui.icon('light_mode', color='gray', size='32px').classes('text-5xl')
                ui_lamp_yard_rear_mode = ui.toggle({1: 'auto', 2: 'on', 3: 'off'}, value=1, on_change=lambda e: light_control.set_relais_mode('yard_rear', e.value)).props('inline')
        with ui.card():
            ui.label("Lampe Hof/Garten").props('inline')
            with ui.row():
                ui_lamp_terrace_state = ui.icon('light_mode', color='gray', size='32px').classes('text-5xl')
                ui_lamp_terrace_mode = ui.toggle({1: 'auto', 2: 'on', 3: 'off'}, value=1, on_change=lambda e: light_control.set_relais_mode('terrasse', e.value)).props('inline')
            ui.slider(min=10, max=100, value=100)
        with ui.card():
            ui.label("Lampe Garage").props('inline')
            with ui.row():
                ui_lamp_garage_state = ui.icon('light_mode', color='gray', size='32px').classes('text-5xl')
                ui_lamp_garage_mode = ui.toggle({1: 'auto', 2: 'on', 3: 'off'}, value=1, on_change=lambda e: light_control.set_relais_mode('garage', e.value)).props('inline')

    with ui.tab_panel(detector).classes('p-1 m-0 gap-1'):
        with ui.card():
            ui.label("Melder Einfahrt").props('inline')
            ui_det_yard = ui.toggle({1: 'active', 2: 'masked'}, value=1, on_change=lambda e: light_control.set_detector('yard', e.value)).props('inline')
        with ui.card():
            ui.label("Melder Hof/Garten").props('inline')
            ui_det_terrasse = ui.toggle({1: 'active', 2: 'masked'}, value=1, on_change=lambda e: light_control.set_detector('terrasse', e.value)).props('inline')
        with ui.card():
            ui.label("Melder Garage").props('inline')
            ui_det_garage = ui.toggle({1: 'active', 2: 'masked'}, value=1, on_change=lambda e: light_control.set_detector('garage', e.value)).props('inline')
        with ui.card():
            ui.label("Lichtsensor Test").props('inline')
            ui.button('Sonnenaufgang', on_click=lambda: light_control.sun.send_event_type(SunEventType.SUN_RISE))
            ui.button('Sonnenuntergang', on_click=lambda: light_control.sun.send_event_type(SunEventType.SUN_SET))

    with ui.tab_panel(energy).classes('p-0 m-0 gap-0'):
        with ui.grid(columns=2).classes('p-1 m-0 gap-1'):
            with ui.card().classes('p-2 m-0'):
                ui.label("Klima Arbeiten + Schlafen").props('inline')
                with ui.knob(color='orange', track_color='grey-2', max = 3500, show_value=True).classes('w-full justify-center') as ui_hvac_a_power:
                    ui.label("W")
                ui_hvac_a_power.disable()
                ui_hvac_a_energy = ui.label("0 kwh").style('color: #6E93D6; font-size: 200%; font-weight: 500')
            with ui.card().classes('p-2 m-0'):
                ui.label("Klima Wohnen + Essen").props('inline')
                with ui.knob(color='orange', track_color='grey-2', max = 3500, show_value=True).classes('w-full justify-center') as ui_hvac_b_power:
                    ui.label("W")
                ui_hvac_b_power.disable()
                ui_hvac_b_energy = ui.label("0 kwh").style('color: #6E93D6; font-size: 200%; font-weight: 500')
            with ui.card().classes('p-2 m-0'):
                ui.label("Klima Mareike + Ralph").props('inline')
                with ui.knob(color='orange', track_color='grey-2', max = 3500, show_value=True).classes('w-full justify-center') as ui_hvac_c_power:
                    ui.label("W")
                ui_hvac_c_power.disable()
                ui_hvac_c_energy = ui.label("0 kwh").style('color: #6E93D6; font-size: 200%; font-weight: 500')
            with ui.card().classes('p-2 m-0'):
                ui.label("Außenbeleuchtung").props('inline')
                with ui.knob(color='orange', track_color='grey-2', max = 3500, show_value=True).classes('w-full justify-center') as ui_light_power:
                    ui.label("W")
                ui_light_power.disable()
                ui_light_energy = ui.label("0 kwh").style('color: #6E93D6; font-size: 200%; font-weight: 500')

        #with ui.card():
            #columns = [
                #{'name': 'meter', 'label': 'Zähler / kwh', 'field': 'meter', 'required': True, 'align': 'left'},
                #{'name': 'day', 'label': 'Tag', 'field': 'day'},
                #{'name': 'week', 'label': 'Woche', 'field': 'week'},
                #{'name': 'month', 'label': 'Monat', 'field': 'month'},
                #{'name': 'year', 'label': 'Jahr', 'field': 'year'},
            #]
            #rows = [
                #{'meter': 'Arbeiten + Schlafen', 'day': 3.25, 'week': 20.31, "month": 71.45, "year": 248.34},
                #{'meter': 'Wohnen + Essen', 'day': 3.25, 'week': 20.31, "month": 71.45, "year": 248.34},
                #{'meter': 'Mareike + Papa', 'day': 3.25, 'week': 20.31, "month": 71.45, "year": 248.34},
                #{'meter': 'Licht', 'day': 0.25, 'week': 2.31, "month": 8.45, "year": 70.34},
            #]
            #ui.table(columns=columns, rows=rows, row_key='name')

def update_ui():
    """Update UI states with I/O modes and states

    I/O is controlled by events and modes and states change automatically.
    This method synchronizes the states and modes from I/O in UI
    """
    ui_det_yard.value = light_control.get_detector('yard')
    ui_det_terrasse.value = light_control.get_detector('terrasse')
    ui_det_garage.value = light_control.get_detector('garage')

    ui_lamp_yard_front_state.props(f"color={light_control.get_relais_state('yard_front')}")
    ui_lamp_yard_rear_state.props(f"color={light_control.get_relais_state('yard_rear')}")
    ui_lamp_terrace_state.props(f"color={light_control.get_relais_state('terrasse')}")
    ui_lamp_garage_state.props(f"color={light_control.get_relais_state('garage')}")

    ui_lamp_yard_front_mode.value = light_control.get_relais_mode('yard_front')
    ui_lamp_yard_rear_mode.value = light_control.get_relais_mode('yard_rear')
    ui_lamp_terrace_mode.value = light_control.get_relais_mode('terrasse')
    ui_lamp_garage_mode.value = light_control.get_relais_mode('garage')

    try:
        ui_hvac_a_power.set_value(round(light_control.meters["hvac-a"].power))
        ui_hvac_a_energy.set_text(f"{round(light_control.meters['hvac-a'].energy, 2)}kwh")
        ui_hvac_b_power.set_value(round(light_control.meters["hvac-b"].power))
        ui_hvac_b_energy.set_text(f"{round(light_control.meters['hvac-b'].energy, 2)}kwh")
        ui_hvac_c_power.set_value(round(light_control.meters["hvac-c"].power))
        ui_hvac_c_energy.set_text(f"{round(light_control.meters['hvac-c'].energy, 2)}kwh")
        ui_light_power.set_value(round(light_control.meters["light"].power))
        ui_light_energy.set_text(f"{round(light_control.meters['light'].energy, 2)}kwh")
    except KeyError:
        pass

async def light_control_main():
    await light_control.io_main()

app.on_startup(light_control_main)

ui.timer(1.0, update_ui)
ui.run(binding_refresh_interval=1, show=False, on_air=False, reload=False)
