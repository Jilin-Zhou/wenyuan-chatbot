import threading
from websocket import WebSocketApp

import config


class BotNav:
    def __init__(self) -> None:
        pass
    def set_goal(self, _) -> tuple[bool, str]:
        print("底盘驱动无效")
    def run(self):
        print("底盘驱动无效")
    def stop(self):
        print("底盘驱动无效")
    def move(self, angular: float, linear: float):
        print("底盘驱动无效")


class BotWS:
    def __init__(self, ws_url, on_msg, on_open, on_close):
        self.on_close_fun = on_close
        self.on_open_fun = on_open
        self.ws = WebSocketApp(
            ws_url, on_message=on_msg, on_open=self.on_open, on_close=self.on_close)
        self.thread = None
        self.connected = False
        self.connecting = False

    def _running(self):
        self.ws.run_forever()
        # self.onCloseFun(self.ws)
        self.connected = False

    def open(self):
        if not self.thread is None:
            return
        self.connecting = True
        self.thread = threading.Thread(target=self._running)
        self.thread.start()

    def close(self):
        self.ws.close()
        if not self.thread is None:
            self.thread.join()
            self.thread = None

    def on_open(self, ws):
        self.connected = True
        self.connecting = False
        self.on_open_fun(ws)

    def on_close(self, ws, state_code, msg):
        self.connected = False
        self.connecting = False
        self.thread = None
        self.on_close_fun(ws, state_code, msg)