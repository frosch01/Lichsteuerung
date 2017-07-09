#!/usr/bin/python3
'''
Documentation, License etc.

@package Lichtsteuerung
'''

from flexx import app, ui, event
from light_control import LightControl, Trigger, Relais, RelaisMode

lightControl = LightControl()

class LightUi(ui.Widget):
    def init(self):
        with ui.BoxLayout(orientation='v'):
            with ui.GroupWidget(title='Lamp yard front'):
                with ui.HBox():
                    self.lampYardFrontButtonAuto = ui.RadioButton(text='auto', checked=True)
                    self.lampYardFrontButtonOn   = ui.RadioButton(text='on')
                    self.lampYardFrontButtonOff  = ui.RadioButton(text='off')
            with ui.GroupWidget(title='Lamp yard rear'):
                with ui.HBox():
                    self.lampYardRearButtonAuto = ui.RadioButton(text='auto', checked=True)
                    self.lampYardRearButtonOn   = ui.RadioButton(text='on')
                    self.lampYardRearButtonOff  = ui.RadioButton(text='off')
            with ui.GroupWidget(title='Lamp terrace'):
                with ui.VBox():
                    with ui.HBox():
                        self.lampTerraceButtonAuto = ui.RadioButton(text='auto', checked=True)
                        self.lampTerraceButtonOn   = ui.RadioButton(text='on')
                        self.lampTerraceButtonOff  = ui.RadioButton(text='off')
                    with ui.HBox():
                        ui.CheckBox(flex=0, text='Dim')
                        self.lampTerraceBrightnessSlider = ui.Slider(flex = 1, min=1, max = 100)
            with ui.GroupWidget(title='Lamp garage'):
                with ui.HBox():
                    self.lampGarageButtonAuto = ui.RadioButton(text='auto', checked = True)
                    self.lampGarageButtonOn   = ui.RadioButton(text='on')
                    self.lampGarageButtonOff  = ui.RadioButton(text='off')
            with ui.GroupWidget(title='Detector yard'):
                with ui.HBox():
                    self.detectorYardButtonActive = ui.RadioButton(text='active', checked = True)
                    self.detectorYardButtonMasked = ui.RadioButton(text='masked')
            with ui.GroupWidget(title='Detector garden'):
                with ui.HBox():
                    self.detectorGardenButtonActive = ui.RadioButton(text='active', checked = True)
                    self.detectorGardenButtonMasked = ui.RadioButton(text='masked')
            with ui.GroupWidget(title='Detector garage'):
                with ui.HBox():
                    self.detectorGarageButtonActive = ui.RadioButton(text='active', checked = True)
                    self.detectorGarageButtonMasked = ui.RadioButton(text='masked')
            ui.Widget(flex=1)
            
    @event.connect('changeLampState')
    def handleStateChange(self, *events):
        ev = events[-1]
        if ev.lamp == 'LampYardFront': relais = Relais.LAMP_WEST
        elif ev.lamp == 'LampYardRear':  relais = Relais.LAMP_SOUTH
        elif ev.lamp == 'LampTerrace':   relais = Relais.LAMP_TERRACE
        elif ev.lamp == 'LampGarage':    relais = Relais.LAMP_NORTH
        else: raise ValueError
                
        if ev.mode == 'on':   mode = RelaisMode.On
        if ev.mode == 'off':  mode = RelaisMode.Off
        if ev.mode == 'auto': mode = RelaisMode.Auto
        
        lightControl.setRelaisMode(relais, mode)

    class JS:

#        @event.connect('b1.mouse_click', 'b2.mouse_click','b3.mouse_click',  )
#        def _button_clicked(self, *events):
#            ev = events[-1]
#            self.buttonlabel.text = 'Clicked on the ' + ev.source.text

        @event.emitter
        def changeLampState(self, js_event):
            return dict(lamp=js_event['lamp'], mode=js_event['mode'])

        @event.connect('lampYardFrontButtonAuto.checked', 
                       'lampYardFrontButtonOn.checked',
                       'lampYardFrontButtonOff.checked')
        def radioLampYardFrontChanged(self, *events):
            ev = events[-1]
            self.changeLampState({'lamp': 'LampYardFront', 'mode': ev.source.text})

        @event.connect('lampYardRearButtonAuto.checked', 
                       'lampYardRearButtonOn.checked',
                       'lampYardRearButtonOff.checked')
        def radioLampYardRearChanged(self, *events):
            ev = events[-1]
            self.changeLampState({'lamp': 'LampYardRear', 'mode': ev.source.text})

        @event.connect('lampTerraceButtonAuto.checked', 
                       'lampTerraceButtonOn.checked',
                       'lampTerraceButtonOff.checked')
        def radioLampTerraceChanged(self, *events):
            ev = events[-1]
            self.changeLampState({'lamp': 'LampTerrace', 'mode': ev.source.text})

        @event.connect('lampGarageButtonAuto.checked', 
                       'lampGarageButtonOn.checked',
                       'lampGarageButtonOff.checked')
        def radioLampGarageChanged(self, *events):
            ev = events[-1]
            self.changeLampState({'lamp': 'LampGarage', 'mode': ev.source.text})

#        @event.connect('c1.checked', 'c2.checked','c3.checked',  )
#        def _check_changed(self, *events):
#            selected = [c.text for c in (self.c1, self.c2, self.c3) if c.checked]
#            if selected:
#                self.checklabel.text = 'Selected: ' + ', '.join(selected)
#            else:
#                self.checklabel.text = 'None selected'


if __name__ == "__main__":
    
    app.create_server(host="0.0.0.0", port=8080)
    m = app.serve(LightUi)
        
    try:
        app.start()
    except:
        pass
        
    print("Terminating LightControl...")
    lightControl.TerminateLoopThread()
    
    print("Terminating Flexx UI...")
    app.stop()
