from enum import Enum
import json
import threading
from time import sleep
import chatie
from config import conf
from xunfei.awaken import Wakeup
from xunfei import iat
from xunfei import tts

# from web.ws_server import ws_server
from web import eel_server

ques = ""
ans = ""

# 状态机相见文档


class State(Enum):
    STOP = -1 # 停止状态
    WAIT = 0  # 等待唤醒
    HEAR = 1  # 收听问题
    SPEAK = 2  # 语音转文本，说话（此过程无法打断）


state = State.STOP


def ivw_callback(sessionID, msg, param1, param2, info, userDate):
    global state
    global ans
    print("wake up")
    if state == State.WAIT:
        ans = "你好"
        state = State.SPEAK
    pass


wakeup_enable = False
voice_wakeup = Wakeup(ivw_callback)
thread: threading.Thread = None
enable = False

busy = False #接口忙

need_break = False #需要打断现有状态
count_down = 0 # 对话超时倒数


def test(ques: str):
    eel_server.send_msg({'type': 'askingText', 'data': ques})
    print('askingText',ques)
    ans = chatie.chat.get_answer(ques)
    eel_server.send_msg({'type':'answerResult', 'data': ans})
    print('answerResult', ans)


# def enableWakeup():

def hear():
    global ques
    ques = iat.run()
    print("问",ques)
    # return ques

def say():
    global ans
    print("答",ans)
    tts.textToSpeech(ans)

def chat_thread():
    global ques
    global ans
    global state
    global need_break
    global count_down
    count_down = 0
    while enable:
        # print(state)


        if state == State.WAIT:
            pass
            if voice_wakeup.thread is None:
                eel_server.send_callback_msg("voiceCondition","waiting")
                voice_wakeup.start()
        else:
            pass
            if not voice_wakeup.thread is None:
                voice_wakeup.stop()
            


        if state == State.HEAR:
            if count_down <= 0:
                if wakeup_enable:
                    state = State.WAIT
                else:
                    state = State.STOP

            eel_server.send_callback_msg("voiceCondition","hearing")
            pass
            hear()

            # 检测是否被打断
            if need_break:
                need_break = False
                continue

            if ques == "":
                if count_down > 0:
                    count_down = count_down - 1
            else:
                eel_server.send_callback_msg("askingText",ques)
                ans = chatie.chat.get_answer(ques)
                count_down = conf.VOICE_TIMEOUT_COUNT
                state = State.SPEAK
        elif state == State.SPEAK:
            if ans != "":
                eel_server.send_callback_msg("voiceCondition","speaking")
                pass
                eel_server.send_callback_msg("answerResult",ans)
                say()
                # 检测是否被打断
                if need_break:
                    need_break = False
                    continue


            state = State.HEAR

        sleep(0.01)
        # print(">")

def start():
    global enable
    global thread
    global state
    global wakeup_enable

    if not thread is None:
        return

    thread = threading.Thread(target=chat_thread)
    enable = True
    if wakeup_enable:
        state = State.WAIT
    else:
        state = State.STOP
    thread.start()

def stop():
    global enable
    global thread
    global state

    enable = False
    state = State.STOP
    voice_wakeup.stop()
    iat.stop()
    tts.stop()

    if thread is None:
        return
    
    thread.join()
    thread = None

def manual_wakeup():
    global state
    pass
    state = State.HEAR

def ask(question: str):
    global ques
    global ans
    global state
    global need_break
    last_state = state
    state = State.STOP
    if last_state != State.STOP and last_state != State.WAIT:
        need_break = True
    if last_state == State.WAIT:
        voice_wakeup.stop()
    elif last_state == State.HEAR:
        iat.stop()
    elif last_state == State.SPEAK:
        tts.stop()

    ques = question
    print("问-",ques)
    eel_server.send_callback_msg("askingText",ques)
    ans = chatie.chat.get_answer(question)
    state = State.SPEAK

def wakeup_control(en: bool):
    global wakeup_enable
    global state
    pass
    wakeup_enable = en
    if en:
        if state == State.STOP:
            state = State.WAIT
    else:
        if state == State.WAIT:
            state = State.STOP

def stop_rec():
    global count_down
    count_down = 0
    iat.stop()
    
    