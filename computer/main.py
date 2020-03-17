from GUI import GUI, mode_dict_set_up, setting_config
from speech_to_text import SpeechToTextController
from arduinoControl import ArduinoController
from threading import Lock
import keyboard as kb
from word2cmd import CommandController
import os

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
        if app.gui.echo:
            kb.write(processed)
        while hotkey != "empty":
            print("hotkey: " + hotkey)
            if hotkey[0] == '\'':
                kb.write(hotkey[1:-1])
            else:
                kb.press(hotkey)
                kb.release(hotkey)
            processed, hotkey, unprocessed = app.commands.find_cmd(app.gui.current_mode, unprocessed)
            if app.gui.echo:
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
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "My-First-Project-958184117e89.json"
        speech_to_text = SpeechToTextController(self, stt_callback)

        self.gui = GUI("gui/", 'settings/GUISetUp.txt', 'settings/settingsGUI.txt', arduino, self.commands,
                       speech_to_text)
        print("Initialized")
        arduino.start()
        speech_to_text.start()
        self.gui.start()


if __name__ == "__main__":
    App()
