from GUI3 import GUI, mode_dict_set_up, setting_config
from speech_to_text import SpeechToTextController
from arduinoControl import ArduinoController
from threading import Lock
import keyboard as kb
from word2cmd import CommandController

mutex = Lock()

def stt_callback(app, text, final):
    if final:
        print("final: " + text)
        app.gui.update_transcript(text)

        # if app.gui.modes[app.gui.current_mode].echo:
        #     print("Final: " + text)
        #     kb.write(text)
        # else:
        processed, hotkey, unprocessed = app.commands.find_cmd(app.gui.current_mode, app.unprocessed + " " + text)
        if app.gui.modes[app.gui.current_mode].echo:
            kb.write(processed)
        while hotkey != "empty":
            print("hotkey: " + hotkey)
            kb.send(hotkey)
            processed, hotkey, unprocessed = app.commands.find_cmd(app.gui.current_mode, unprocessed)
            if app.gui.modes[app.gui.current_mode].echo:
                kb.write(processed)

        app.unprocessed = unprocessed
    else:
        print("Potential: " + text)
        app.gui.update_transcript(text)


class App:

    def __init__(self):
        self.unprocessed = ""
        self.commands = CommandController()
        # self.commands.load_cmds("format", 'backend/cmds_format.txt')
        arduino = ArduinoController()
        arduino.start()
        speech_to_text = SpeechToTextController(self, stt_callback)
        speech_to_text.start()

        self.gui = GUI("gui/", 'settings/GUISetUp.txt', 'settings/settingsGUI.txt', arduino, self.commands, speech_to_text)
        print("Initialized")
        self.gui.start()


if __name__ == "__main__":
    app = App()