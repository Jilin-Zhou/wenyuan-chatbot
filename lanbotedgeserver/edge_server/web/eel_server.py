import os
import json
import yaml
import eel
import bottle
from bottle import request, response

import voice
import xunfei
from web import eel_server

from config import conf

app = bottle.Bottle()


@app.route(conf.WEB_STATIC2_URL + '/<path:path>')
def static2(path: str):
    print("static2 path =>", path)
    return bottle.static_file(path, root=conf.WEB_STATIC2_PATH)


@app.route('/api/config/<name>')
def get_config(name):
    if name.find(".") != -1:
        return {'ok': False, 'errMsg': '文件名错误'}, 400
    try:
        fs = open(os.path.join(conf.WEB_CONFIG_PATH,
                               name+".yaml"), encoding="UTF-8")
        datas = yaml.safe_load(fs)
        fs.close()
    # except FileNotFoundError:
    #     return {'ok': False, 'errMsg': '文件不存在'}, 400
    except Exception as e:
        return {'ok': False, 'errMsg': str(e)}, 400
    return {'ok': True, 'data': datas}


@app.route('/api/voice/chatControl')
def chat_control():
    if not conf.VOICE_EN:
        return {'ok': False, 'errMsg': "该后端不支持"}, 400

    args = request.query
    print(args['enable'])
    if args['enable'] == "true":
        voice.chat.start()
    else:
        voice.chat.stop()
    return {'ok': True}


@app.route('/api/voice/wakeupControl')
def wakeup_control():
    if not conf.VOICE_EN:
        return {'ok': False, 'errMsg': "该后端不支持"}, 400

    args = request.query
    print(args['enable'])
    voice.chat.wakeup_control(args['enable'] == "true")
    return {'ok': True}


@app.route('/api/voice/manualWakeup')
def manual_wakeup():
    if not conf.VOICE_EN:
        return {'ok': False, 'errMsg': "该后端不支持"}, 400
    voice.chat.manual_wakeup()
    return {'ok': True}


@app.route('/api/voice/stopRecording')
def stop_recording():
    if not conf.VOICE_EN:
        return {'ok': False, 'errMsg': "该后端不支持"}, 400
    voice.chat.stop_rec()
    return {'ok': True}


@app.route('/api/voice/ask')
def ask():
    if voice.chat.busy:
        return {'ok': False, 'errMsg': "后端忙"}, 400
    args = request.query.decode("utf-8")

    if not conf.VOICE_EN:
        voice.chat.test(args['question'])
        return {'ok': False, 'errMsg': "语音已禁用，进入测试模式"}, 400

    # eel_server.send_msg("test")

    voice.chat.busy = True
    voice.chat.ask(args['question'])
    voice.chat.busy = False
    return {'ok': True }


@app.route('/api/voice/tts/speak')
def tts_speak():
    if voice.chat.enable:
        return {'ok': False, 'errMsg': "对话状态下无法使用该接口"}, 400
    args = request.query.decode("utf-8")

    if not conf.VOICE_EN:
        return {'ok': False, 'errMsg': "语音已禁用，进入测试模式"}, 400

    
    voice.tts.start_tts_thread(args['text'])
    return {'ok': True}


@app.route('/api/voice/tts/stop')
def tts_stop():
    if voice.chat.enable:
        return {'ok': False, 'errMsg': "对话状态下无法使用该接口"}, 400

    if not conf.VOICE_EN:
        return {'ok': False, 'errMsg': "语音已禁用，进入测试模式"}, 400

    xunfei.tts.stop()
    print("STOP")
    return {'ok': True}

@app.route('/test')
def hello():
    return { 'msg': "HelloWorld" }


def start_browser():
    # Docker环境中不启动浏览器，只运行API服务
    if os.environ.get('DOCKER_ENV') == 'true' or not conf.VOICE_EN:
        print("Docker环境或语音已禁用，跳过浏览器启动，只运行API服务")
        # 启动Bottle API服务器
        app.run(host='0.0.0.0', port=20550)
    else:
        eel.init(conf.ROOT_PATH+'./resources/dist')
        eel.start('/index.html', app=app, cmdline_args=['--start-fullscreen'])

def send_callback_msg(msgType, data):
    eel.js_onmessage({'type': msgType, 'data': data})
