import os
from ctypes import c_int, cdll, byref, c_void_p, CFUNCTYPE, c_char_p, c_uint64, c_int64
import threading
from types import FunctionType
import xunfei.audio as xf_audio
from config import conf


# def py_ivw_callback(sessionID, msg, param1, param2, info, userDate):
#     # typedef int( *ivw_ntf_handler)( const char *sessionID, int msg, int param1, int param2, const void *info, void *userData );
#     # 在此处编辑唤醒后的动作
#     print("sessionID =>", sessionID)
#     print("msg =>", msg)
#     print("param1 =>", param1)
#     print("param2 =>", param2)
#     print("info =>", info)
#     print("userDate =>", userDate)


CALLBACKFUNC = CFUNCTYPE(None, c_char_p, c_uint64,
                         c_uint64, c_uint64, c_void_p, c_void_p)
# pCallbackFunc = CALLBACKFUNC(py_ivw_callback)


class Wakeup():

    def __init__(self,cb_fun: FunctionType = None):
        self.wait = True
        self.thread = None
        self.cbFun = self.none_callback if cb_fun is None else cb_fun

    def ivw_wakeup(self):
        p_callback_func = CALLBACKFUNC(self.cbFun)
        try:
            msc_load_library = conf.XF_MSC_LIB
            app_id = conf.XF_APPID  # 'dd2359a2'# 填写自己的app_id
            ivw_threshold = '0:1450'
            jet_path = conf.XF_JET
            workDir = 'fo|' + jet_path
        except Exception as e:
            return e

        # ret 成功码
        MSP_SUCCESS = 0

        dll = cdll.LoadLibrary(msc_load_library)
        error_code = c_int64()
        session_id = c_void_p()
        # MSPLogin
        login_params = "appid={},engine_start=ivw".format(app_id)
        login_params = bytes(login_params, encoding="utf8")
        ret = dll.MSPLogin(None, None, login_params)
        if MSP_SUCCESS != ret:
            print("MSPLogin failed, error code is:", ret)
            return

        # QIVWSessionBegin
        begin_params = "sst=wakeup,ivw_threshold={},ivw_res_path={}".format(
            ivw_threshold, workDir)
        begin_params = bytes(begin_params, encoding="utf8")
        dll.QIVWSessionBegin.restype = c_char_p
        session_id = dll.QIVWSessionBegin(None, begin_params, byref(error_code))
        if MSP_SUCCESS != error_code.value:
            print("QIVWSessionBegin failed, error code is: {}".format(
                error_code.value))
            return

        # QIVWRegisterNotify
        dll.QIVWRegisterNotify.argtypes = [c_char_p, c_void_p, c_void_p]
        ret = dll.QIVWRegisterNotify(session_id, p_callback_func, None)
        if MSP_SUCCESS != ret:
            print("QIVWRegisterNotify failed, error code is: {}".format(ret))
            return

        # QIVWAudioWrite
        recorder = xf_audio.Recorder()
        dll.QIVWAudioWrite.argtypes = [c_char_p, c_void_p, c_uint64, c_int64]
        ret = MSP_SUCCESS
        print("* start recording")
        while ret == MSP_SUCCESS and self.wait:
            audio_data = b''.join(recorder.get_record_audio())
            audio_len = len(audio_data)
            ret = dll.QIVWAudioWrite(session_id, audio_data, audio_len, 2)
        print('QIVWAudioWrite ret =>{}', ret)
        print("* done recording")


        dll.QIVWSessionEnd.restype = c_int
        ret = dll.QIVWSessionEnd(session_id, "Normal")
        if MSP_SUCCESS != ret:
            print("QIVWSessionEnd failed, error code:",ret)
        
        # recorder.__del__()
        dll.MSPLogout()
        

    def start(self):
        self.thread = threading.Thread(target=self.ivw_wakeup)
        self.wait = True
        self.thread.start()

    def stop(self):
        self.wait = False
        if not self.thread is None:
            self.thread.join()
        self.thread = None

    def none_callback(self):
        pass


if __name__ == '__main__':
    wakeup = Wakeup()
    wakeup.ivw_wakeup()
