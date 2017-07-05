#!/usr/bin/python3
'''
Documentation, License etc.

@package Lichtsteuerung
'''

from flexx import app, ui, event

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
            with ui.GroupWidget(title='Lamp garden'):
                with ui.VBox():
                    with ui.HBox():
                        self.lampGardenButtonAuto = ui.RadioButton(text='auto', checked=True)
                        self.lampGardenButtonOn   = ui.RadioButton(text='on')
                        self.lampGardenButtonOff  = ui.RadioButton(text='off')
                    with ui.HBox():
                        ui.CheckBox(flex=0, text='Dim')
                        self.lampGardenBrightnessSlider = ui.Slider(flex = 1, min=1, max = 100)
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

if __name__ == '__main__':
    app.create_server(host="0.0.0.0", port=8080)
    m = app.serve(LightUi)
    app.start()
