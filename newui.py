import datetime
import asyncio
from nicegui import app, ui
from nicegui.events import ValueChangeEventArguments
from light_control_new import LightControl
from sun import SunEvent, SunEventType

def root():
    def update_ui():
        """Update UI states with I/O modes and states

        I/O is controlled by events and modes and states change automatically.
        This method synchronizes the states and modes from I/O in UI
        """
        try:
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

            ui_hvac_a_power.set_value(round(light_control.meters["hvac-a"].power))
            ui_hvac_a_energy.set_text(f"{round(light_control.meters['hvac-a'].energy, 2)}kwh")
            ui_hvac_b_power.set_value(round(light_control.meters["hvac-b"].power))
            ui_hvac_b_energy.set_text(f"{round(light_control.meters['hvac-b'].energy, 2)}kwh")
            ui_hvac_c_power.set_value(round(light_control.meters["hvac-c"].power))
            ui_hvac_c_energy.set_text(f"{round(light_control.meters['hvac-c'].energy, 2)}kwh")
            ui_light_power.set_value(round(light_control.meters["light"].power))
            ui_light_energy.set_text(f"{round(light_control.meters['light'].energy, 2)}kwh")
            ui_dim_terrace.set_value(light_control.dim.duty)
        except KeyError:
            pass
        except NameError:
            pass

    def update_calib(event):
        if event.value:
            ui_calib_hvac_a.value = light_control.meters['hvac-a'].energy
            ui_calib_hvac_b.value = light_control.meters['hvac-b'].energy
            ui_calib_hvac_c.value = light_control.meters['hvac-c'].energy
            ui_calib_light.value = light_control.meters['light'].energy

    ui.timer(1.0, update_ui)

    with ui.tabs() as tabs:
        light = ui.tab('Licht')
        wau = ui.tab('Fluffy')
        detector = ui.tab('Melder')
        hvac = ui.tab('Klima')
        solar = ui.tab('Solar')

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
                ui_dim_terrace = ui.slider(min=10, max=100, value=100, on_change=lambda e: light_control.dim.set_duty(e.value))
            with ui.card():
                ui.label("Lampe Garage").props('inline')
                with ui.row():
                    ui_lamp_garage_state = ui.icon('light_mode', color='gray', size='32px').classes('text-5xl')
                    ui_lamp_garage_mode = ui.toggle({1: 'auto', 2: 'on', 3: 'off'}, value=1, on_change=lambda e: light_control.set_relais_mode('garage', e.value)).props('inline')

        with ui.tab_panel(wau).classes('p-1 m-0 gap-1'):
            with ui.card():
                ui.label("Fluffy").props('inline')
                ui_wau_mode = ui.toggle({1: 'auto', 2: 'off', 3: 'test'}, value=1).props('inline')
                #, on_change=lambda e: light_control.set_relais_mode('garage', e.value)).props('inline')
            with ui.card():
                global time_wau_on
                global time_wau_max
                time_wau_on = 0
                time_wau_max = 1

                def set_wau_timeout(t):
                    now = datetime.datetime.now().time()
                    diff = (t.hour - now.hour) * 60 + t.minute - now.minute
                    if diff < 0:
                        diff += 24*60
                    if diff == 0:
                        return
                    global time_wau_on
                    global time_wau_max
                    time_wau_on = diff
                    time_wau_max = diff
                    wau_on_lp.set_value(1)

                def wau_dec_timeout():
                    global time_wau_on
                    global time_wau_max
                    if time_wau_on:
                        time_wau_on -= 1
                        wau_on_lp.set_value(round(time_wau_on / time_wau_max, 2))
                    else:
                        now = datetime.datetime.now().time()
                        wau_silent_time.set_value(f"{now.hour:02}:{now.minute:02}")
                        wau_on_lp.set_value(0)

                ui.label("reactivate").props('inline')
#                ui.select(options = [
#                    '0 (off)',
#                    '0.01 (kurz)',
#                    '1 Stunde',
#                    '2 Stunden',
#                    '3 Stunden',
#                    '5 Stunden',
#                    '8 Stunden',
#                    '13 Stunden',
#                    '21 Stunden',
#                ], with_input=True, value = '0 (off)', on_change=lambda e: set_wau_timeout(float(e.value.split(' ')[0]) * 3600)) \
#                .classes('w-40') \
#                .props('inline')
                now = datetime.datetime.now().time()
                wau_silent_time = ui.time(
                    value=f"{now.hour:02}:{now.minute:02}",
                    on_change=lambda e: set_wau_timeout(datetime.time.fromisoformat(e.value))
                )
                ui.label("remaining").props('inline')
                wau_on_lp = ui.linear_progress(value=0).props('label-always').props('inline')
                ui.timer(60, wau_dec_timeout)

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

        with ui.tab_panel(hvac).classes('p-0 m-0 gap-0'):
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

            with ui.card().classes('p-1 m-1 gap-1'):
                ui_calib_cb = ui.checkbox("Kalibrierung", on_change = update_calib)
                with ui.grid(columns=2).bind_visibility_from(ui_calib_cb, 'value'):
                    ui.label("Zähler links")
                    ui_calib_hvac_c = ui.number(label="HVAC-C", format='%.2f', on_change=lambda e: light_control.meters['hvac-c'].set_energy(e.value))
                    ui.label("Zähler mitte")
                    ui_calib_hvac_b = ui.number(label="HVAC-B", format='%.2f', on_change=lambda e: light_control.meters['hvac-b'].set_energy(e.value))
                    ui.label("Zähler rechts")
                    ui_calib_hvac_a = ui.number(label="HVAC-A", format='%.2f', on_change=lambda e: light_control.meters['hvac-a'].set_energy(e.value))
                    ui.label("Zähler Licht")
                    ui_calib_light = ui.number(label="Licht", format='%.2f', on_change=lambda e: light_control.meters['light'].set_energy(e.value))

        with ui.tab_panel(solar).classes():
            ui.element('iframe')\
                .props('src="http://ekrano.fritz.box:"').classes('w-[calc(78vw)] h-[calc(47vw)]')

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
                #ui.table(columns=columns, rows=rows, row_key='name').classes('w-full justify-center')

async def light_control_main():
    await light_control.io_main()


# MAGIC...
# The code found herein is NOT MAIN. The complete module is based on local
# storage and everything is re-constructed as browser reloads. To make
# LightControl instance persisten, it is created as part of app object.
if not app.is_started:
    app.light_control = LightControl()
    app.on_startup(light_control_main)
light_control = app.light_control

ui.run(root, binding_refresh_interval=1, show=False, on_air=False, reload=False)
