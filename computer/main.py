from GUI3 import GUI, mode_dict_set_up, setting_config
from speech_to_text import SpeechToTextController
from threading import Lock
import keyboard as kb

mutex = Lock()

def stt_callback(app, text, final):
    mutex.acquire()
    try:
        if final:
            print("Final: " + text)
        else:
            print("Potential: " + text)
            app.gui.uppdate_transcript(text)
    finally:
        mutex.release()

class App:

    def __init__(self):
        modes = mode_dict_set_up('gui/GUISetUp.txt')
        settings = setting_config('gui/settingsGUI.txt')
        self.gui = GUI(modes, settings)
        print("Initialized")
        controller = SpeechToTextController(self, stt_callback)
        controller.start()

        kb.wait("escape")

if __name__ == "__main__":
    app = App()
