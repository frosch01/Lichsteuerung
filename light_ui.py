#!/usr/bin/python3
'''
Documentation, License etc.

@package Lichtsteuerung
'''

from flexx import app, ui, event
from light_control import LightControl, Detector, DetectorMode, Relais, RelaisMode, Pwm

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
                    self.detectorTerraceButtonActive = ui.RadioButton(text='active', checked = True)
                    self.detectorTerraceButtonMasked = ui.RadioButton(text='masked')
            with ui.GroupWidget(title='Detector garage'):
                with ui.HBox():
                    self.detectorGarageButtonActive = ui.RadioButton(text='active', checked = True)
                    self.detectorGarageButtonMasked = ui.RadioButton(text='masked')
            ui.Widget(flex=1)
            
    @event.connect('changeLampMode')
    def handleLampModeChange(self, *events):
        ev = events[-1]
        if   ev.lamp == 'LampYardFront': relais = Relais.LAMP_WEST
        elif ev.lamp == 'LampYardRear':  relais = Relais.LAMP_SOUTH
        elif ev.lamp == 'LampTerrace':   relais = Relais.LAMP_TERRACE
        elif ev.lamp == 'LampGarage':    relais = Relais.LAMP_NORTH
        else: raise ValueError                
        if   ev.mode == 'on':   mode = RelaisMode.On
        elif ev.mode == 'off':  mode = RelaisMode.Off
        elif ev.mode == 'auto': mode = RelaisMode.Auto
        else: raise ValueError                
        lightControl.setRelaisMode(relais, mode)

    @event.connect('changeDetectorMode')
    def handleDetectorModeChange(self, *events):
        ev = events[-1]
        if   ev.detector == 'DetectorYard':    detector = Detector.MOTION_SENSE_SOUTH
        elif ev.detector == 'DetectorTerrace': detector = Detector.MOTION_SENSE_TERRACE
        elif ev.detector == 'DetectorGarage':  detector = Detector.MOTION_SENSE_NORTH
        else: raise ValueError
        if   ev.mode == 'active':  mode = DetectorMode.Active
        elif ev.mode == 'masked':  mode = DetectorMode.Masked
        else: raise ValueError                
        lightControl.setDetectorMode(detector, mode)
        
    @event.connect('changeBrightness')
    def handleBrightnessChange(self, *events):
        ev = events[-1]
        if ev.lamp == 'LampTerrace':  lamp = Pwm.LAMP_TERRACE
        else: raise ValueError
        lightControl.setPwm(lamp, ev.value)
        
    class JS:

        @event.emitter
        def changeLampMode(self, js_event):
            return dict(lamp=js_event['lamp'], mode=js_event['mode'])

        @event.emitter
        def changeDetectorMode(self, js_event):
            return dict(detector=js_event['detector'], mode=js_event['mode'])

        @event.emitter
        def changeBrightness(self, js_event):
            return dict(lamp=js_event['lamp'], value=js_event['value'])

        @event.connect('lampYardFrontButtonAuto.checked', 
                       'lampYardFrontButtonOn.checked',
                       'lampYardFrontButtonOff.checked')
        def radioLampYardFrontChanged(self, *events):
            ev = events[-1]
            self.changeLampMode({'lamp': 'LampYardFront', 'mode': ev.source.text})

        @event.connect('lampYardRearButtonAuto.checked', 
                       'lampYardRearButtonOn.checked',
                       'lampYardRearButtonOff.checked')
        def radioLampYardRearChanged(self, *events):
            ev = events[-1]
            self.changeLampMode({'lamp': 'LampYardRear', 'mode': ev.source.text})

        @event.connect('lampTerraceButtonAuto.checked', 
                       'lampTerraceButtonOn.checked',
                       'lampTerraceButtonOff.checked')
        def radioLampTerraceChanged(self, *events):
            ev = events[-1]
            self.changeLampMode({'lamp': 'LampTerrace', 'mode': ev.source.text})

        @event.connect('lampGarageButtonAuto.checked', 
                       'lampGarageButtonOn.checked',
                       'lampGarageButtonOff.checked')
        def radioLampGarageChanged(self, *events):
            ev = events[-1]
            self.changeLampMode({'lamp': 'LampGarage', 'mode': ev.source.text})

        @event.connect('detectorYardButtonActive.checked', 
                       'detectorYardButtonMasked.checked')
        def radioDetectorYardChanged(self, *events):
            ev = events[-1]
            self.changeDetectorMode({'detector': 'DetectorYard', 'mode': ev.source.text})

        @event.connect('detectorTerraceButtonActive.checked', 
                       'detectorTerraceButtonMasked.checked')
        def radioDetectorTerraceChanged(self, *events):
            ev = events[-1]
            self.changeDetectorMode({'detector': 'DetectorTerrace', 'mode': ev.source.text})

        @event.connect('detectorGarageButtonActive.checked', 
                       'detectorGarageButtonMasked.checked')
        def radioDetectorGarageChanged(self, *events):
            ev = events[-1]
            self.changeDetectorMode({'detector': 'DetectorGarage', 'mode': ev.source.text})

        @event.connect('lampTerraceBrightnessSlider.value')
        def sliderChangeBrightness(self, *events):
            ev = events[-1]
            self.changeBrightness({'lamp': 'LampTerrace', 'value': ev.new_value})

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
