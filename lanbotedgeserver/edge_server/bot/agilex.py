import requests

import config


def _get(url: str, params: dict):
    r = requests.get(config.agilex.URL_PREFIX+url, params=params)
    return r.json()


def move(angular: float, linear: float):
    """
    移动控制
    :param angular:  角速度
    :param linear:   线速度
    """
    return _get("/cmdMove",
                params={
                    'speed': {
                        'angularSpeed': angular,
                        'linearSpeed':  linear
                    }

                })


# 导航相关

def navigate(map_name: str, position_name: str):
    """前往目标点"""
    return _get("/gs-robot/cmd/position/navigate",
                params={'map_name': map_name, 'position_name': position_name})
