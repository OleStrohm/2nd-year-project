from GUI3 import GUI, mode_dict_set_up, setting_config
from speech_to_text import SpeechToTextController
from arduinoControl import ArduinoController
from threading import Lock
import keyboard as kb
from word2cmd import CommandController

mutex = Lock()


def stt_callback(app, text, final):
    mutex.acquire()
    try:
        if final:
            app.gui.uppdate_transcript(text)
            if app.gui.modes[app.gui.current_mode].echo:
                print("Final: " + text)
            else:
                hotkey, unprocessed = app.commands.find_cmd(app.gui.current_mode, app.unprocessed + " " + text)
                while hotkey is not "empty":
                    kb.press(hotkey)
                    hotkey, unprocessed = app.commands.find_cmd(app.gui.current_mode, unprocessed)
                app.unprocessed = unprocessed
        else:
            print("Potential: " + text)
            app.gui.uppdate_transcript(text)
    finally:
        mutex.release()


class App:

    def __init__(self):
        self.unprocessed = ""
        self.commands = CommandController()
        self.commands.load_cmds("format", 'backend/cmds_format.txt')
        arduino = ArduinoController()
        arduino.start()
        textToSpeech = SpeechToTextController(self, stt_callback)
        textToSpeech.start()
        modes = mode_dict_set_up('gui/GUISetUp.txt')
        settings = setting_config('gui/settingsGUI.txt')
        self.gui = GUI(modes, settings, "")
        print("Initialized")

    def on_close(self):
        pass


if __name__ == "__main__":
    app = App()
    kb.wait("escape")
