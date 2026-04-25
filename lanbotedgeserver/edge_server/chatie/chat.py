import requests

import config


def get_answer(question: str) -> str:
    """获取问题答案或聊天结果"""
    # print("question",question)
    try:
        res = requests.get(config.chatie.API_URL, params={
            "question": question,
            "conf_name": config.chatie.CHAT_CONF_NAME,
        },timeout=30)
    except Exception as e:
        print("get_answer",e)
        return ""
    print(res)
    return res.text

    
