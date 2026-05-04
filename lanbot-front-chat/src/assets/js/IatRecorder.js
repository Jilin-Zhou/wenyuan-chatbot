const APPID = '' //在科大讯飞控制台中获取的服务接口认证信息
const API_SECRET = '' //在科大讯飞控制台中获取的服务接口认证信息
const API_KEY = '' //在科大讯飞控制台中获取的服务接口认证信息
import CryptoJS from 'crypto-js'
var socket

function getWebSocketUrl(){
  return new Promise((resolve, reject) => {
    // 请求地址根据语种不同变化
    var url = 'wss://iat-api.xfyun.cn/v2/iat'
    var host = 'iat-api.xfyun.cn'
    var apiKey = API_KEY
    var apiSecret = API_SECRET
    var date = new Date().toGMTString()
    var algorithm = 'hmac-sha256'
    var headers = 'host date request-line'
    var signatureOrigin = `host: ${host}\ndate: ${date}\nGET /v2/iat HTTP/1.1`
    var signatureSha = CryptoJS.HmacSHA256(signatureOrigin, apiSecret)
    var signature = CryptoJS.enc.Base64.stringify(signatureSha)
    var authorizationOrigin = `api_key="${apiKey}", algorithm="${algorithm}", headers="${headers}", signature="${signature}"`
    var authorization = btoa(authorizationOrigin)
    url = `${url}?authorization=${authorization}&date=${date}&host=${host}`
    resolve(url)
  })
}

const IatRecorder = class {
  constructor({ language, accent, appId } = {}) {
    this.language = language || 'zh_cn';
    this.accent = accent || 'mandarin';
    this.appId = appId || APPID;
    // 记录音频数据
    this.mediaData = [];
    //Base64编码的音频数据
    this.base64Data = '';
    // //json格式的音频对象
    // this.jsonCode = '';
    // 记录听写结果
    this.resultText = '';
    // wpgs下的听写结果需要中间状态辅助记录
    this.resultTextTemp = '';

    this.mediaRecorder;

    //发送帧的状态
    this.state = 0;
  }
  
  setResultText({ resultText, resultTextTemp } = {}) {
    this.onTextChange && this.onTextChange(resultTextTemp || resultText || '')
    resultText !== undefined && (this.resultText = resultText)
    resultTextTemp !== undefined && (this.resultTextTemp = resultTextTemp)
  }
  connectWebSocket () {
    getWebSocketUrl()
      .then((url) => {
        socket = new WebSocket(url);
        // console.log("socket:" + socket);
        // this.setStatus('init');
        socket.addEventListener('open', (event) => {
          // this.setStatus('ing');
          console.log('WebSocket连接已打开');
          this.recorderStart();
        });

        socket.addEventListener('message', (event) => {
          console.log("处理接收到的消息")
          console.log(event)
          // 处理接收到的消息
          let jsonData = JSON.parse(event.data);
          console.log(jsonData.data)
          console.log(jsonData.data.result)
          if (jsonData.data && jsonData.data.result) {
            console.log("识别到信息")
            let data = jsonData.data.result;
            let str = '';
            let ws = data.ws;
            for (let i = 0; i < ws.length; i++) {
              str = str + ws[i].cw[0].w;
            }
            console.log("识别的结果为：", str);
            // 开启wpgs会有此字段(前提：在控制台开通动态修正功能)
            // 取值为 "apd"时表示该片结果是追加到前面的最终结果；取值为"rpl" 时表示替换前面的部分结果，替换范围为rg字段
            if (data.pgs) {
              if (data.pgs === 'apd') {
                // 将resultTextTemp同步给resultText
                this.setResultText({
                  resultText: this.resultTextTemp,
                });
              }
              // 将结果存储在resultTextTemp中
              this.setResultText({
                resultTextTemp: this.resultText + str,
              });
            } else {
              this.setResultText({
                resultText: this.resultText + str,
              });
            }
          }
        });

        socket.addEventListener('close', (event) => {
          console.log('WebSocket连接已关闭');
          // 在这里执行与WebSocket关闭相关的操作
        });

        socket.addEventListener('error', (event) => {
          console.error('WebSocket发生错误:', event);
          // 在这里处理WebSocket错误
        });
      })
      .catch((error) => {
        console.error('获取WebSocket URL时发生错误:', error);
      });
  }
  // 开始录音
  recorderStart () {
    // 获取音频流
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then((stream) => {
        // 创建MediaRecorder对象
        this.mediaRecorder = new MediaRecorder(stream);
        //限制录音时间
        this.mediaRecorder.addEventListener('start', () => {
            // timerId = setTimeout(() => {
            //   this.mediaRecorder.stop();
            //   this.state = 2;
            //   clearTimeout(timerId);
            // }, 300000);
        });

        // 监听dataavailable事件，将录制的数据块存储到数组中
        this.mediaRecorder.addEventListener('dataavailable', (event) => {
          this.mediaData = [];
          this.mediaData.push(event.data);
          console.log("发送音频")
          
          //console.log(event.data)
          //console.log(this.mediaData)
          //console.log(this.mediaData);
          // 创建Blob对象，将录制的数据块合并为一个音频文件
          const audioBlob = new Blob(this.mediaData, { type: this.mediaRecorder.mimeType });
          // 使用FileReader将音频文件转换为Base64编码
          const fileReader = new FileReader();
          fileReader.readAsDataURL(audioBlob);
          fileReader.onloadend = () => {
            this.base64Data = fileReader.result.split(',')[1];
            console.log('this.base64Data.length = ' + this.base64Data.length);
            // 发送json格式的音频数据
            console.log('this.state = ' + this.state);
            if (this.base64Data.length != 0) {
              if (this.state == 0) {
                var params = {
                  common: {
                    app_id: this.appId,
                  },
                  business: {
                    language: this.language, //小语种可在控制台--语音听写（流式）--方言/语种处添加试用
                    domain: 'iat',
                    accent: this.accent, //中文方言可在控制台--语音听写（流式）--方言/语种处添加试用
                  },
                  data: {
                    status: 0,
                    format: 'audio/L16;rate=16000',
                    encoding: 'raw',
                    audio: this.base64Data,
                  },
                }
                console.log("START");
                socket.send(JSON.stringify(params));
                this.state++;
              }
              if (this.state == 1) {
                params = {
                  data: {
                    status: 1,
                    format: 'audio/L16;rate=16000',
                    encoding: 'raw',
                    audio: this.base64Data,
                  },
                }
                console.log("CONTENT");
                //console.log(this.base64Data);
                socket.send(JSON.stringify(params));
              }
            } 
            if (this.state == 2) {
              params = {
                data: {
                  status: 2,
                  format: 'audio/L16;rate=16000',
                  encoding: 'raw',
                  audio: this.base64Data,
                },
              }
              this.state = 0;
              console.log("END");
              socket.send(JSON.stringify(params));
            }
          }

        });

        // 监听stop事件，在录制结束后处理录制的音频数据
        this.mediaRecorder.addEventListener('stop', () => {
          //clearTimeout(timerId);
        });

        // 开始录制
        this.mediaRecorder.start(3000);

      })
      .catch((error) => {
        console.error('获取音频流失败:', error);
      });
  }
  // 暂停录音
  recorderStop () {
    this.mediaRecorder.stop();
  }


  start () {
    this.connectWebSocket();
    this.resultText = '';
    this.resultTextTemp = '';
  }
  stop() {
    this.recorderStop();
    this.state = 2;
  }
};
export default IatRecorder
