from flask import Flask
from flask_cors import CORS
from gpt import chat
from chat.query import most_sim_ques
from flask import request

app = Flask(__name__)
CORS(app)  # 启用跨域支持

@app.route('/chatbot/api/v1.0/get', methods=['GET'])
def get_chatbot_response():
    original_question = request.args.get('question')
    try:
        sim_ques,sim_ans = most_sim_ques(original_question)
        context = f"可供参考相关问题:<<<{sim_ques}>>>\n对应的参考答案:<<<{sim_ans}>>>\n"
        prompt = context + f"Q:<<<{original_question}>>>"
    except:
        context = f"可供参考相关问题:<<<None>>>\n对应的参考答案:<<<None>>>\n"
        prompt = context + f"Q:<<<{original_question}>>>"
    
    res = chat(query=prompt)
    print("Answer:", res) 
    return res


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=1090)
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)

