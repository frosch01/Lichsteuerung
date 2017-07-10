#!/usr/bin/python3
'''
Documentation, License etc.

@package light_control
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
            
    def getRelaisModeFromText(self, text):
        if   text == 'on':   mode = RelaisMode.On
        elif text == 'off':  mode = RelaisMode.Off
        elif text == 'auto': mode = RelaisMode.Auto
        else: raise ValueError
        return mode
    
    def getDetectorModeFromText(self, text):
        if   text == 'active':  mode = DetectorMode.Active
        elif text == 'masked':  mode = DetectorMode.Masked
        else: raise ValueError
        return mode
            
    @event.connect('lampYardFrontButtonAuto.checked', 
                   'lampYardFrontButtonOn.checked',
                   'lampYardFrontButtonOff.checked')
    def radioLampYardFrontChanged(self, *events):
        ev = events[-1]
        if (ev.new_value):
            mode = self.getRelaisModeFromText(ev.source.text)
            lightControl.setRelaisMode(Relais.LAMP_WEST, mode)
            
    @event.connect('lampYardRearButtonAuto.checked', 
                   'lampYardRearButtonOn.checked',
                   'lampYardRearButtonOff.checked')
    def radioLampYardRearChanged(self, *events):
        ev = events[-1]
        if (ev.new_value):
            mode = self.getRelaisModeFromText(ev.source.text)
            lightControl.setRelaisMode(Relais.LAMP_SOUTH, mode)

    @event.connect('lampTerraceButtonAuto.checked', 
                   'lampTerraceButtonOn.checked',
                   'lampTerraceButtonOff.checked')
    def radioLampTerraceChanged(self, *events):
        ev = events[-1]
        if (ev.new_value):
            mode = self.getRelaisModeFromText(ev.source.text)
            lightControl.setRelaisMode(Relais.LAMP_TERRACE, mode)

    @event.connect('lampGarageButtonAuto.checked', 
                   'lampGarageButtonOn.checked',
                   'lampGarageButtonOff.checked')
    def radioLampGarageChanged(self, *events):
        ev = events[-1]
        if (ev.new_value):
            mode = self.getRelaisModeFromText(ev.source.text)
            lightControl.setRelaisMode(Relais.LAMP_NORTH, mode)

    @event.connect('detectorYardButtonActive.checked', 
                   'detectorYardButtonMasked.checked')
    def radioDetectorYardChanged(self, *events):
        ev = events[-1]
        if (ev.new_value):
            mode = self.getDetectorModeFromText(ev.source.text)
            lightControl.setDetectorMode(Detector.MOTION_SENSE_SOUTH, mode)

    @event.connect('detectorTerraceButtonActive.checked', 
                   'detectorTerraceButtonMasked.checked')
    def radioDetectorTerraceChanged(self, *events):
        ev = events[-1]
        if (ev.new_value):
            mode = self.getDetectorModeFromText(ev.source.text)
            lightControl.setDetectorMode(Detector.MOTION_SENSE_TERRACE, mode)

    @event.connect('detectorGarageButtonActive.checked', 
                   'detectorGarageButtonMasked.checked')
    def radioDetectorGarageChanged(self, *events):
        ev = events[-1]
        if (ev.new_value):
            mode = self.getDetectorModeFromText(ev.source.text)
            lightControl.setDetectorMode(Detector.MOTION_SENSE_NORTH, mode)

    @event.connect('lampTerraceBrightnessSlider.value')
    def sliderChangeBrightness(self, *events):
        ev = events[-1]
        lightControl.setPwm(Pwm.LAMP_TERRACE, ev.new_value)

        
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
