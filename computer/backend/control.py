import keyboard as kb
from gg_rt_rec import SpeechToTextController

def stt_callback(text, final):
    if final:
        kb.write(text)
    else:
        print("Potential: " + text)

if __name__ == "__main__":
    # move (90.0, 100)
    # cmd = Macro("test", [Left(5), Text("teext"), Right(2), Text("more")])
    controller = SpeechToTextController(stt_callback)
    controller.start()
    kb.wait("escape")
    #cmd.execute()
# ---------------------------------S------------------------------------
