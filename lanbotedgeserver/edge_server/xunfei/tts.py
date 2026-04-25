from ctypes import c_int, c_void_p, cdll, byref, string_at,  c_char_p
import threading
from time import sleep

import xunfei.audio as xf_audio
from xunfei import sdk
from config import conf
import voice

wait = False
app_id = sdk.app_id
running = False


def textToSpeech(txt: str = ""):
    """语音转文本"""

    global wait
    global running
    dll = sdk.dll
    wait = True
    running = True

    if txt == "":
        return
    # ret 码
    MSP_SUCCESS = 0
    MSP_TTS_FLAG_DATA_END = 2

    error_code = c_int()
    session_id = c_void_p()
    # MSPLogin
    login_params = "appid={},work_dir=.".format(app_id)
    login_params = bytes(login_params, encoding="utf8")
    ret = dll.MSPLogin(None, None, login_params)
    if MSP_SUCCESS != ret:
        print("MSPLogin failed, error code is:", ret)
        return

    # QTTSSessionBegin
    begin_params = "voice_name=xiaoyan,text_encoding=UTF8,sample_rate=16000,speed=40,volume=50,pitch=50,rdn=0"
    begin_params = bytes(begin_params, encoding="utf8")
    dll.QTTSSessionBegin.restype = c_char_p
    session_id = dll.QTTSSessionBegin(begin_params, byref(error_code))
    if MSP_SUCCESS != error_code.value:
        print("QTTSSessionBegin failed, error code is: {}".format(
            error_code.value))
        return

    # QTTSTextPut
    txt_bytes = bytes(txt, encoding="utf8")
    ret = dll.QTTSTextPut(session_id, txt_bytes, len(txt_bytes), None)
    if MSP_SUCCESS != ret:
        print("QTTSTextPut failed, error code: {}.\n".format(ret))
        dll.QTTSSessionEnd(session_id, "TextPutError")
        return

    # print("正在合成 ...")
    print("* start playing")
    player = xf_audio.Player()
    while wait:
        audio_len = c_int()
        synth_status = c_int()
        dll.QTTSAudioGet.restype = c_void_p
        data_p = dll.QTTSAudioGet(session_id, byref(
            audio_len), byref(synth_status), byref(error_code))
        # print("data_p",data_p)
        # print("audio_len",audio_len.value)
        if MSP_SUCCESS != error_code.value:
            break

        # print(">", end="")

        data = string_at(data_p, audio_len.value)

        player.play_audio(data)

        if MSP_TTS_FLAG_DATA_END == synth_status.value:
            break

    # print()

    # print('QTTSAudioGet ret =>', errorCode.value)
    print("* done playing")
    # player.__del__()

    dll.QTTSSessionEnd.restype = c_int
    ret = dll.QTTSSessionEnd(session_id, "Normal")
    if MSP_SUCCESS != ret:
        print("QTTSSessionEnd failed, error code:", ret)

    dll.MSPLogout()

    running = False


def stop():
    global wait
    global running
    wait = False
    while running:
        pass
        sleep(0.01)
