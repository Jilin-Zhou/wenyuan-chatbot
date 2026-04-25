import imp
# Docker环境中pyaudio可能不可用，使用try-except处理
try:
    from xunfei import audio
    from xunfei import awaken
    from xunfei import tts
    XUNFEI_AVAILABLE = True
except ImportError as e:
    print(f"讯飞语音模块导入失败: {e}")
    XUNFEI_AVAILABLE = False
    audio = None
    awaken = None
    tts = None

from xunfei import sdk