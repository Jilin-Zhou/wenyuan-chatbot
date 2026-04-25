<script>
export default {
    name: 'HomeView',
    components: {
  
    },
    mounted() {
  
      this.audioInit()
    },
    methods: {
      audioInit() {
        // 初始化语音转写
        let startBtn = document.getElementById("startBtn")
        // 结束按钮
        let endBtn = document.getElementById("endBtn")
        // 接收识别的文本
        let output = document.getElementById("output")
        // 记时器
        let time = document.getElementById("time")
        // 如果使用的是webpack,或者报错 请尝试这种写法  const recorderWorker = new Worker('../assets/js/transformpcm.worker.js')
        const recorderWorker = new Worker(new URL('../utils/transformpcm.worker.js', import.meta.url))
        // 记录处理的缓存音频
        let buffer = []
        let AudioContext = window.AudioContext || window.webkitAudioContext
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia
  
        recorderWorker.onmessage = function (e) {
          buffer.push(...e.data.buffer)
        }
  
        class IatRecorder {
          constructor(config) {
            this.config = config
            this.state = 'ing'
  
            //以下信息在控制台-我的应用-实时语音转写 页面获取
            this.appId = '9c333155'
            this.apiKey = 'b1f959680aed18191436235f8ecc7e75'
          }
  
          start() {
            this.stop()
            if (navigator.getUserMedia && AudioContext) {
              this.state = 'ing'
              if (!this.recorder) {
                var context = new AudioContext()
                this.context = context
                console.log(context)
                this.recorder = context.createScriptProcessor(0, 1, 1)
  
                var getMediaSuccess = (stream) => {
                  var mediaStream = this.context.createMediaStreamSource(stream)
                  this.mediaStream = mediaStream
                  this.recorder.onaudioprocess = (e) => {
                    this.sendData(e.inputBuffer.getChannelData(0))
                  }
                  this.connectWebsocket()
                }
                var getMediaFail = (e) => {
                  this.recorder = null
                  this.mediaStream = null
                  this.context = null
                  console.log('请求麦克风失败')
                  alert("请求麦克风失败")
                }
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                  navigator.mediaDevices.getUserMedia({
                    audio: true,
                    video: false
                  }).then((stream) => {
                    console.log(stream)
                    getMediaSuccess(stream)
                  }).catch((e) => {
                    console.log(e)
                    getMediaFail(e)
                  })
                } else {
                  navigator.getUserMedia({
                    audio: true,
                    video: false
                  }, (stream) => {
                    getMediaSuccess(stream)
                  }, function (e) {
                    console.log(e)
                    getMediaFail(e)
                  })
                }
              } else {
                this.connectWebsocket()
              }
            } else {
              var isChrome = navigator.userAgent.toLowerCase().match(/chrome/)
              alert("暂不支持使用该浏览器,请使用chrome浏览器")
            }
          }
  
          stop() {
            this.state = 'end'
            try {
              this.mediaStream.disconnect(this.recorder)
              this.recorder.disconnect()
            } catch (e) { }
          }
  
          sendData(buffer) {
            recorderWorker.postMessage({
              command: 'transform',
              buffer: buffer
            })
          }
          // 生成握手参数
          getHandShakeParams() {
            var appId = this.appId
            var secretKey = this.apiKey
            var ts = Math.floor(new Date().getTime() / 1000);//new Date().getTime()/1000+'';
            var signa = hex_md5(appId + ts)//hex_md5(encodeURIComponent(appId + ts));//EncryptUtil.HmacSHA1Encrypt(EncryptUtil.MD5(appId + ts), secretKey);
            var signatureSha = CryptoJSNew.HmacSHA1(signa, secretKey)
            var signature = CryptoJS.enc.Base64.stringify(signatureSha)
            signature = encodeURIComponent(signature)
            return "?appid=" + appId + "&ts=" + ts + "&signa=" + signature + '&pd=court';
          }
          connectWebsocket() {
            var url = 'wss://rtasr.xfyun.cn/v1/ws'
            var urlParam = this.getHandShakeParams()
            
            url = `${url}${urlParam}`
            if ('WebSocket' in window) {
              this.ws = new WebSocket(url)
            } else if ('MozWebSocket' in window) {
              this.ws = new MozWebSocket(url)
            } else {
              alert(notSupportTip)
              return null
            }
            this.ws.onopen = (e) => {
              this.mediaStream.connect(this.recorder)
              this.recorder.connect(this.context.destination)
              setTimeout(() => {
                this.wsOpened(e)
              }, 500)
              this.config.onStart && this.config.onStart(e)
            }
            this.ws.onmessage = (e) => {
              // this.config.onMessage && this.config.onMessage(e)
              this.wsOnMessage(e)
            }
            this.ws.onerror = (e) => {
              this.stop()
              console.log("关闭连接ws.onerror");
              this.config.onError && this.config.onError(e)
            }
            this.ws.onclose = (e) => {
              this.stop()
              console.log("关闭连接ws.onclose");
              // $('.start-button').attr('disabled', false);
              this.config.onClose && this.config.onClose(e)
            }
          }
  
          wsOpened() {
            if (this.ws.readyState !== 1) {
              return
            }
            var audioData = buffer.splice(0, 1280)
            this.ws.send(new Int8Array(audioData))
            this.handlerInterval = setInterval(() => {
              // websocket未连接
              if (this.ws.readyState !== 1) {
                clearInterval(this.handlerInterval)
                return
              }
              if (buffer.length === 0) {
                if (this.state === 'end') {
                  this.ws.send("{\"end\": true}")
                  console.log("发送结束标识");
                  clearInterval(this.handlerInterval)
                }
                return false
              }
              var audioData = buffer.splice(0, 1280)
              if (audioData.length > 0) {
                this.ws.send(new Int8Array(audioData))
              }
            }, 40)
          }
  
          wsOnMessage(e) {
            let jsonData = JSON.parse(e.data)
            if (jsonData.action == "started") {
              // 握手成功
              console.log("握手成功");
            } else if (jsonData.action == "result") {
              // 转写结果
              if (this.config.onMessage && typeof this.config.onMessage == 'function') {
                this.config.onMessage(jsonData.data)
              }
            } else if (jsonData.action == "error") {
              // 连接发生错误
              console.log("出错了:", jsonData);
              alert("连接发发生错误")
            }
          }
  
  
          ArrayBufferToBase64(buffer) {
            var binary = ''
            var bytes = new Uint8Array(buffer)
            var len = bytes.byteLength
            for (var i = 0; i < len; i++) {
              binary += String.fromCharCode(bytes[i])
            }
            return window.btoa(binary)
          }
        }
  
        class IatTaste {
          constructor() {
            var iatRecorder = new IatRecorder({
              onClose: () => {
                this.stop()
                this.reset()
              },
              onError: (data) => {
                this.stop()
                this.reset()
                alert('WebSocket连接失败')
              },
              onMessage: (message) => {
                this.setResult(JSON.parse(message))
              },
              onStart: () => {
                this.counterDown(time)
              }
            })
            this.iatRecorder = iatRecorder
            this.counterDownDOM = time
            this.counterDownTime = 0
          }
          start() {
            this.iatRecorder.start()
          }
  
          stop() {
            this.iatRecorder.stop()
          }
  
          reset() {
            this.counterDownTime = 0
            clearTimeout(this.counterDownTimeout)
            buffer = []
  
          }
  
          init() {
            let self = this
            //开始按钮的事件
            startBtn.onclick = function () {
              if (navigator.getUserMedia && AudioContext && recorderWorker) {
                self.start()
              } else {
                alert(notSupportTip)
              }
            }
  
            //结束按钮的事件
            endBtn.onclick = function () {
              self.stop()
              //reset
              this.counterDownTime = 0
              clearTimeout(this.counterDownTimeout)
              buffer = []
            }
          }
  
          // 转写的结果
          setResult(data) {
            let rtasrResult = []
            rtasrResult[data.seg_id] = data
            rtasrResult.forEach(i => {
              let str = ""
              if (i.cn.st.type == 0) {
                i.cn.st.rt.forEach(j => {
                  j.ws.forEach(k => {
                    k.cw.forEach(l => {
                      str += l.w
                    })
                  })
                })
                console.log(output.value,str)
                console.log(str)
                if(str != '。' && str != '?'&& str != '?') {
                    output.value += str
                }
              }
  
            })
          }
  
          // 计时器
          counterDown() {
            if (this.counterDownTime >= 0 && this.counterDownTime < 10) {
              this.counterDownDOM.innerText = '00: 0' + this.counterDownTime
            } else if (this.counterDownTime >= 10 && this.counterDownTime < 60) {
              this.counterDownDOM.innerText = '00: ' + this.counterDownTime
            } else if (this.counterDownTime % 60 >= 0 && this.counterDownTime % 60 < 10) {
              this.counterDownDOM.innerText = '0' + parseInt(this.counterDownTime / 60) + ': 0' + this.counterDownTime % 60
            } else {
              this.counterDownDOM.innerText = '0' + parseInt(this.counterDownTime / 60) + ': ' + this.counterDownTime % 60
            }
            this.counterDownTime++
            this.counterDownTimeout = setTimeout(() => {
              this.counterDown()
            }, 1000)
          }
        }
        var iatTaste = new IatTaste()
        iatTaste.init()
      }
    }
  }

</script>


<template>
  <div class="home">
      <button id="startBtn">
      开始
    </button>
    <button id="endBtn">
      结束
    </button>
    <div id="output"></div>
    <div id="time" v-show="false">00: 00</div>
  </div>
</template>


<style>

</style>