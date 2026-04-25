from config import conf
from ctypes import cdll

app_id = conf.XF_APPID  # 'dd2359a2'# 填写自己的app_id
dll = None
def init():
    """SDK初始化（程序运行后仅需执行一次）"""
    global dll
    mscLoadLibrary = conf.XF_MSC_LIB
    dll = cdll.LoadLibrary(mscLoadLibrary)
    # print(dll)