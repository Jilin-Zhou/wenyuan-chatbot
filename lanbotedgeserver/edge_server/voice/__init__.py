# Docker环境中pyaudio可能不可用，使用try-except处理
try:
    from voice import chat
    from voice import tts
    VOICE_AVAILABLE = True
except ImportError as e:
    print(f"语音模块导入失败（Docker环境可能不支持音频设备）: {e}")
    VOICE_AVAILABLE = False
    # 创建空的模块引用，避免其他代码报错
    chat = None
    tts = None
