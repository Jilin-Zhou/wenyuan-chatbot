from ctypes import c_int, cdll, byref, c_void_p, CFUNCTYPE, c_char_p, c_uint64, c_int64, string_at
from time import sleep

import xunfei.audio as xf_audio
from config import conf
from xunfei import sdk

wait = False
thread = None
app_id = sdk.app_id

running = False


def run():
    """
    启动语音听写，可手动或自动停止
    """
    global app_id
    global wait
    global running
    wait = True
    running = True
    dll = sdk.dll
    rec_result = ""

    # ret 码
    MSP_SUCCESS = 0
    MSP_REC_STATUS_SUCCESS = 0
    MSP_EP_AFTER_SPEECH = 3
    MSP_REC_STATUS_COMPLETE = 5

    MSP_AUDIO_SAMPLE_FIRST = 1
    MSP_AUDIO_SAMPLE_CONTINUE = 2
    MSP_AUDIO_SAMPLE_LAST = 4

    error_code = c_int64()
    session_id = c_void_p()
    # MSPLogin
    login_params = "appid={},work_dir=.".format(app_id)
    login_params = bytes(login_params, encoding="utf8")
    ret = dll.MSPLogin(None, None, login_params)
    if MSP_SUCCESS != ret:
        print("MSPLogin failed, error code is:", ret)
        return rec_result

    # QISRSessionBegin
    begin_params = "sub=iat,domain=iat,language=zh_cn,accent=mandarin,sample_rate=16000,result_type=plain,result_encoding=utf8,vad_eos=1000"
    begin_params = bytes(begin_params, encoding="utf8")
    dll.QISRSessionBegin.restype = c_char_p
    session_id = dll.QISRSessionBegin(None, begin_params, byref(error_code))
    if MSP_SUCCESS != error_code.value:
        print("QISRSessionBegin failed, error code is: {}".format(
            error_code.value))
        return rec_result
    # QISRAudioWrite
    dll.QISRAudioWrite.restype = c_int
    recorder = xf_audio.Recorder(RECORD_TIME=0.25)
    print("* start recording")

    ret = MSP_SUCCESS
    audio_status = MSP_AUDIO_SAMPLE_CONTINUE
    ep_stat = c_int()
    rec_stat = c_int()
    while ret == MSP_SUCCESS and wait:
        # print(0)
        audio_data = b''.join(recorder.get_record_audio())
        audio_len = len(audio_data)
        # print(1)
        ret = dll.QISRAudioWrite(
            session_id, audio_data, audio_len, audio_status, byref(ep_stat), byref(rec_stat))
        # print(2)
        if ret != MSP_SUCCESS:
            print("QISRAudioWrite failed! error code:", ret)
            break

        if MSP_REC_STATUS_SUCCESS == rec_stat.value:
            dll.QISRGetResult.restype = c_char_p
            rslt = dll.QISRGetResult(
                session_id, byref(rec_stat), 0, byref(error_code))
            if error_code.value != MSP_SUCCESS:
                print("QISRGetResult failed! error code:", error_code.value)
                break
            if None != rslt:
                rec_result += str(string_at(rslt), "utf8")

        if MSP_EP_AFTER_SPEECH == ep_stat.value:
            break

        # print(">")

    # print('QISRAudioWrite ret =>{}', ret)
    print("* done recording")

    ret = dll.QISRAudioWrite(
        session_id, None, 0, MSP_AUDIO_SAMPLE_LAST, byref(ep_stat), byref(rec_stat))

    if ret != MSP_SUCCESS:
        print("QISRAudioWrite failed! error code:", ret)

    while MSP_REC_STATUS_COMPLETE != rec_stat.value:
        dll.QISRGetResult.restype = c_char_p
        rslt = dll.QISRGetResult(
            session_id, byref(rec_stat), 0, byref(error_code))
        if MSP_SUCCESS != error_code.value:
            print("QISRGetResult failed, error code:", error_code.value)
            break
        if None != rslt:
            rec_result += str(string_at(rslt), "utf8")

    dll.QISRSessionEnd.restype = c_int
    ret = dll.QISRSessionEnd(session_id, "Normal")
    if MSP_SUCCESS != ret:
        print("QISRSessionEnd failed, error code:", ret)

    # recorder.__del__()
    dll.MSPLogout()

    running = False

    return rec_result


def stop():
    """停止语音听写"""
    global wait
    global running
    wait = False
    while running:
        pass
        sleep(0.01)
