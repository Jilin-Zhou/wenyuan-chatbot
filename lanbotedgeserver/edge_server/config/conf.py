from enum import Enum
import os
import platform
from dotenv import load_dotenv, find_dotenv
from config import conf

ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")

load_dotenv(verbose=True,override=True)

def get_env_default(name, default):
    return os.environ.get(name, default)



# 讯飞部分
XF_APPID = "21f70064"#更新于2024.5.23
XF_MSC_LIB = ROOT_PATH + "/bin/xunfei/msc_x64.dll"
XF_JET = ROOT_PATH + "/resources/wakeupresource.wenyuan.jet"

WEB_DIST_PATH = ROOT_PATH +"/resources/dist/"
WEB_DIST_URL = "/"
WEB_STATIC2_PATH = ROOT_PATH +"/resources/static2"  # 静态资源文件路径
WEB_STATIC2_URL = "/static2"  # 静态资源文件URL

WEB_CONFIG_PATH = ROOT_PATH +"./resources/config"  # 配置文件路径
WEB_PATH = ROOT_PATH +"./resources/dist"  # 编译后的前端文件路径

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 20550

WS_SERVER_PORT = SERVER_PORT + 1

# 底盘部分
class BotEnum(Enum):
    AGILEX = 0
    SMART = 1

BOT_TYPE = BotEnum.SMART

VOICE_EN = platform.system().lower() == 'windows'
VOICE_TIMEOUT_COUNT = 2