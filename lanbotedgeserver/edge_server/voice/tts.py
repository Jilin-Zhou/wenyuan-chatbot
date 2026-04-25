import threading

from time import sleep
from xunfei.tts import textToSpeech, stop
import xunfei
import voice
# from web.ws_server import ws_server
from web import eel_server

tts_thread: threading.Thread = None

isSpeaking = False

def tts_fun(txt: str):
    global isSpeaking
    textToSpeech(txt)
    if not voice.chat.enable and xunfei.tts.wait:
        # eel_server.send_callback_msg("finishSpeaking","")
        isSpeaking = False
        # ws_server.send_callback_msg("finishSpeaking","")


def start_tts_thread(text: str):
    global isSpeaking
    if isSpeaking:
        stop()
        print("STOP")
        sleep(0.5)
    isSpeaking = True
    global tts_thread
    tts_thread = threading.Thread(target=tts_fun,args=[text])
    tts_thread.start()