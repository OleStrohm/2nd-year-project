from GUI3 import GUIController
from speech_to_text import SpeechToTextController
import keyboard as kb

global gui
gui = None

def stt_callback(text, final):
    global gui
    if final:
        print("Final: " + text)
    else:
        print("Potential: " + text)
        gui.uppdate_transcript(text)

if __name__ == "__main__":
    guiController = GUIController("gui/GUISetUp.txt", "gui/settingsGUI.txt")
    while not guiController.initialized:
        pass
    print("Initialized")
    gui = guiController.gui
    controller = SpeechToTextController(stt_callback)
    controller.start()

    kb.wait("escape")
# ---------------------------------S------------------------------------
