import base64
import gzip
import json
import threading
from time import sleep
import requests
from websocket import WebSocketApp
# from ctypes import c_bool, c_int, cdll, byref, c_void_p, CFUNCTYPE, c_char_p, c_uint64, c_int64, string_at, windll

import config
# from web.ws_server import ws_server
from web import eel_server
from bot.model import BotNav
from bot.model import BotWS


"""
SDK
"""

# CALLBACKFUNC = CFUNCTYPE(c_int, c_int64, c_char_p)

# def callbackFunc(iMsgID, dwDataLen, pBuff):
#     """回调函数"""
#     print("cbFun:", iMsgID, dwDataLen, pBuff)
#     return 0


# class SDK():
#     def __init__(self) -> None:
#         self.dll = windll.LoadLibrary(config.smart.SDK_LIB)

#     def initDll(self):
#         self.dll.InitDll.restype = c_bool
#         return self.dll.InitDll(0,1,200,bytes(config.smart.STR_IP,"utf8"),0)

#     def setCallBackFun(self, pCallbackFunc):
#         pCallbackFunc = CALLBACKFUNC(callbackFunc)
#         self.dll.SetCallBackFun(pCallbackFunc)

#     def releaseDll(self):
#         self.dll.ReleaseDll.restype = c_bool
#         return self.dll.ReleaseDll()


"""
web api
"""


# def _post(url: str, data: dict = {}):
#     r = None
#     ok = False
#     try:
#         res = requests.post(config.smart.URL_PREFIX+url,
#                             json=data, timeout=15)
#         r = res.json()
#         ok = res.status_code == 200
#     except requests.exceptions.ConnectTimeout:
#         r = "底盘连接超时"
#     except Exception as e:
#         r = str(e)
#     print(ok, r)
#     return ok, r

def _get(url: str, data: dict = {}) -> tuple[bool, str]:
    r = None
    ok = False
    try:
        res = requests.get(config.smart.URL_PREFIX+url,
                           params={"msg": json.dumps(data)}, timeout=3)
        res_json = res.json()
        print(res_json)
        result_txt = res_json['result']
        if result_txt != "":
            try:
                r = json.loads(result_txt)
            except:
                r = result_txt
        ok = res_json['type'] == url
    except requests.exceptions.ConnectTimeout:
        r = "底盘连接超时"
    except Exception as e:
        r = str(e)
    # print(ok, r)
    return ok, r

# 普通控制


def cmd_move(angular: float, linear: float) -> tuple[bool, str]:
    """
    移动控制
    :param angular:  角速度
    :param linear:   线速度
    """
    return _get("/cmdMove",
                data={
                    'angular': {'x': 0.0, 'y': 0.0, 'z': angular},
                    'linear': {'x': linear, 'y': 0.0, 'z': 0.0}
                })


def recharge_ctrl(enable: bool):
    """回充控制"""
    return _get("/rechargeCtrl",
                data={"data": 1 if enable else 0})


# 导航

def navigation_imu_start():
    """开启导航服务"""
    global nav_service_en
    nav_service_en = True
    return _get("/navigationImuStart")


def navigation_imu_stop():
    """关闭导航服务"""
    return _get("/navigationImuStop")


def set_current_goal(goal_name: str):
    """设置目标点"""
    return _get("/setCurrentGoal",
                data={"is_continue": False, "goal_name": goal_name})


def start_nav_goal():
    """开始导航"""
    return _get("/startNavGoal")


def stop_nav_goal():
    """停止导航"""
    return _get("/stopNavGoal")


def get_nav_service_state():
    """获取导航服务状态"""
    ok, r = process_state()
    if not ok:
        return ok, r
    return ok, int(r['navigationImu'])


class SmartNav(BotNav):
    def __init__(self):
        self._goal_name = ""

    def set_goal(self, name: str) -> tuple[bool, str]:
        ok, nav_state = res = get_nav_service_state()
        if not ok:
            return res
        if not nav_state > 0:
            return False, "导航服务未启动"
            # ok,_ = res = smart.navigationImuStart()
            # print("navigationImuStart", res)
            # if not ok:
            #     return res

        self._goal_name = name
        res = set_current_goal(name)
        print("setCurrentGoal", res)
        return res

    def run(self):
        ok, nav_state = res = get_nav_service_state()
        if not ok:
            return res
        if not nav_state > 0:
            return False, "导航服务未启动"
            # ok,_ = res = smart.navigationImuStart()
            # print("navigationImuStart", res)
            # if not ok:
            #     return res

        # if self._goalName == "":
        #     return False,""
        res = start_nav_goal()
        print("startNavGoal", res)
        return res

    def stop(self):
        res = stop_nav_goal()
        return res

    def move(self, angular: float, linear: float) -> tuple[bool, str]:
        res = cmd_move(angular, linear)
        return res


nav = SmartNav()


"""
状态相关
"""


def process_state():
    """获取ros状态"""
    return _get("/processState")


ws_enable = True


def encode(data: dict) -> bytes:
    return base64.b64encode(gzip.compress(json.dumps(data).encode()))


def decode(data: str) -> dict:
    return json.loads(gzip.decompress(base64.b64decode(data)))


def ws_on_message(ws, msg):
    data = decode(msg)
    # print("wsOnMessage", data)
    data_type = data['type']
    data_res = ""
    try:
        data_res = json.loads(data['result'])
    except Exception as e:
        data_res = data['result']
        print("error ws_on_message",data_res)
        return
    # print(dataRes)
    if data_type == "getNavResult":
        nav_status = data_res['status']['status']
        if nav_status == 3:
            print("目标已到达")
            eel_server.send_callback_msg(
                'navResult', {'type': 'reachGoal', 'goalName': nav._goal_name})
        elif nav_status == 4:
            print("导航失败")
            eel_server.send_callback_msg('navResult', {'type': 'fail'})


def ws_on_open(ws: WebSocketApp):
    print("smart ws connected")
    msg = {
        "type": "getNavResult",  # 数据订阅类型
        "throttle_rate": 0,  # 数据接收频率 毫秒
    }
    ws.send(encode(msg))


def ws_on_close(ws, stateCode=None, msg=None):
    print("smart ws closed")
    pass


smart_ws = BotWS(config.smart.WS_URL, ws_on_message, ws_on_open, ws_on_close)

ws_check_loop_thread: threading.Thread = None


def ws_check_loop():
    global ws_enable
    global ws_check_loop_thread
    global smart_ws
    COUNT_MAX = 100
    count = 0
    while ws_enable:
        pass
        if smart_ws.connected:
            count += 1
            if count > COUNT_MAX:
                count = 0
                print("ws client 发送订阅请求")
                msg = {
                    "type": "getNavResult",  # 数据订阅类型
                    "msg": "", 
                }
                smart_ws.ws.send(encode(msg))
        else:
            if not smart_ws.connecting:
                print("smart ws connecting")
                smart_ws.open()
        sleep(0.1)


def enable_ws():
    pass
    global ws_enable
    global ws_check_loop_thread
    global smart_ws
    ws_enable = True
    smart_ws.open()
    ws_check_loop_thread = threading.Thread(
        target=ws_check_loop, name="ws_check_loop")
    ws_check_loop_thread.start()


def disable_ws():
    pass
    global ws_enable
    global ws_check_loop_thread
    global smart_ws
    ws_enable = False
    if not ws_check_loop_thread is None:
        ws_check_loop_thread.join()
    smart_ws.close()
