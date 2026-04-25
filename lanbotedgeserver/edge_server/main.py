import sys
import signal
import os


import websocket

from config import conf
import voice

from xunfei import sdk

from web import eel_server

from chatie import chat

from bot import driver

# 检查语音模块是否可用
VOICE_AVAILABLE = voice.VOICE_AVAILABLE if hasattr(voice, 'VOICE_AVAILABLE') else True
if VOICE_AVAILABLE:
    from voice.chat import voice_wakeup

stopping = False

def stop_handler():
    global stopping
    if stopping:
        return
    stopping = True
    print("停止中")
    if VOICE_AVAILABLE:
        voice_wakeup.stop()
    total = 2
    print("%d/%d" % (1, total))
    driver.disable_ws_client()
    print("%d/%d" % (2, total))
    if VOICE_AVAILABLE and voice.chat:
        voice.chat.stop()
    print("程序退出")
    stopping = False
    sys.exit(0)

if __name__ == "__main__":
    # 初始化
    print("初始化,启动中")
    try:
        if conf.VOICE_EN:
            sdk.init()
        websocket.setdefaulttimeout(2)  # 设置websocket超时时间
        eel_server.start_browser()
    except Exception as e:
        print(e)
        pass
    finally:
        stop_handler()

    

