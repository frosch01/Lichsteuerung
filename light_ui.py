#!/usr/bin/python3
'''
Documentation, License etc.

@package light_control
'''

from flexx import app, ui, event
from light_control import LightControl, Detector, DetectorMode, Relais, RelaisMode, Pwm

lightControl = LightControl()

class StatusView(ui.Widget):
    def init(self):
         print(self.base_size)
         
class LampRadioButton(ui.RadioButton):
    def __init__(self, lamp, mode, **kwargs):
        self.lamp = lamp
        self.mode = mode
        super().__init__(**kwargs)
        if mode == lightControl.getRelaisMode(lamp):
            self.checked = True
            
class LampRadioHBox(ui.HBox):
    def __init__(self, uniqName, lamp, **kwargs):
        self.uniqName = uniqName
        self.lamp = lamp
        super().__init__(**kwargs)
    def init(self):
        super().init()
        self.addConnectedButton('ButtonAuto', LampRadioButton(self.lamp, RelaisMode.Auto, text='auto', parent = self))
        self.addConnectedButton('ButtonOn',   LampRadioButton(self.lamp, RelaisMode.On,   text='on',   parent = self))
        self.addConnectedButton('ButtonOff',  LampRadioButton(self.lamp, RelaisMode.Off,  text='off',  parent = self))
    def addConnectedButton(self, buttonName, button):
        attrName = '%s%s' % (buttonName, self.uniqName)
        setattr(self, attrName, button)
        self.connect(self.radioLampChanged, attrName + '.checked')
    def radioLampChanged(self, *events):
        ev = events[-1]
        if (ev.new_value):
            mode = events[-1].source.mode
            lamp = events[-1].source.lamp
            lightControl.setRelaisMode(lamp, mode)
    
class DetectorRadioButton(ui.RadioButton):
    def __init__(self, detector, mode, **kwargs):
        self.detector = detector
        self.mode = mode
        super().__init__(**kwargs)
        if mode == lightControl.getDetectorMode(detector):
            self.checked = True

class DetectorRadioHBox(ui.HBox):
    def __init__(self, uniqName, detector, **kwargs):
        self.uniqName = uniqName
        self.detector = detector
        super().__init__(**kwargs)
    def init(self):
        super().init()
        self.addConnectedButton('ButtonActive', DetectorRadioButton(self.detector, DetectorMode.Active, text='active', parent = self))
        self.addConnectedButton('ButtonMasked', DetectorRadioButton(self.detector, DetectorMode.Masked, text='masked', parent = self))
    def addConnectedButton(self, buttonName, button):
        attrName = '%s%s' % (buttonName, self.uniqName)
        setattr(self, attrName, button)
        self.connect(self.radioDetectorChanged, attrName + '.checked')
    def radioDetectorChanged(self, *events):
        ev = events[-1]
        if (ev.new_value):
            mode = events[-1].source.mode
            detector = events[-1].source.detector
            lightControl.setDetectorMode(detector, mode)

class LightUi(ui.Widget):
    def init(self):
        with ui.BoxLayout(orientation='v'):
            with ui.GroupWidget(title='Lamp yard front'):
                LampRadioHBox('lampYardFront', Relais.LAMP_WEST)
            with ui.GroupWidget(title='Lamp yard rear'):
                LampRadioHBox('lampYardRear', Relais.LAMP_SOUTH)
            with ui.GroupWidget(title='Lamp terrace'):
                with ui.VBox():
                    LampRadioHBox('lampTerrace', Relais.LAMP_TERRACE)
                    with ui.HBox():
                        ui.CheckBox(flex=0, text='Dim')
                        self.lampTerraceBrightnessSlider = ui.Slider(flex = 1, min=1, max = 100)
            with ui.GroupWidget(title='Lamp garage'):
                LampRadioHBox('lampGarage', Relais.LAMP_NORTH)
            with ui.GroupWidget(title='Detector yard'):
                DetectorRadioHBox('detectorYard', Detector.MOTION_SENSE_SOUTH)
            with ui.GroupWidget(title='Detector garden'):
                DetectorRadioHBox('detectorTerrace', Detector.MOTION_SENSE_TERRACE)
            with ui.GroupWidget(title='Detector garage'):
                DetectorRadioHBox('detectorGarage', Detector.MOTION_SENSE_NORTH)
            StatusView()
            ui.Widget(flex=1)
            
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
