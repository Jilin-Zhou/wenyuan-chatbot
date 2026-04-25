<script>
import IatRecorder from '@/assets/js/IatRecorder.js'
import axios from 'axios'
import { WS_ADDRESS, API_ADDRESS } from '@/configs/index.js'

const iatRecorder = new IatRecorder('zh_cn', 'mandarin', '9c33315')

export default {
  data() {
    return {
      // 预设问题列表
      items: [
        { message: '北京有哪些好玩的地方?', num: 1 },
        { message: '北京北站怎么走?', num: 2 },
        { message: '故宫门票多少钱?', num: 3 }
      ],

      // 消息列表
      messageList: [],
      
      // WebSocket对象
      webSocketObject: null,
      wsConnected: false,
      
      // 当前问题和回答
      currentQuestion: '',
      currentAnswer: '您好，我是文渊问答助手。请问有什么能帮您的？',
      
      // 加载状态
      isLoading: false,

      // 录音相关
      searchData: '',
      state: 0,
      statename: '开始录音',
      timerId: 0,
    }
  },
  
  created() {
    // 初始化WebSocket连接
    this.webSocketInit()
  },
  
  methods: {
    // ==================== WebSocket 相关 ====================
    
    webSocketInit() {
      console.log('正在连接WebSocket:', WS_ADDRESS)
      try {
        this.webSocketObject = new WebSocket(WS_ADDRESS)
        
        this.webSocketObject.onopen = (e) => {
          console.log('WebSocket连接成功', e)
          this.wsConnected = true
        }
        
        this.webSocketObject.onmessage = (e) => {
          console.log('收到WebSocket消息', e.data)
          try {
            const data = JSON.parse(e.data)
            this.handleWebSocketMessage(data)
          } catch (err) {
            console.error('消息解析失败:', err)
          }
        }
        
        this.webSocketObject.onerror = (e) => {
          console.error('WebSocket连接错误', e)
          this.wsConnected = false
        }
        
        this.webSocketObject.onclose = (e) => {
          console.log('WebSocket连接关闭', e)
          this.wsConnected = false
        }
      } catch (err) {
        console.error('WebSocket初始化失败:', err)
      }
    },
    
    handleWebSocketMessage(data) {
      if (data.type === 'askingText') {
        this.currentQuestion = data.data
        this.messageList.push({ type: 'question', text: data.data })
      } else if (data.type === 'answerResult') {
        this.currentAnswer = data.data
        this.isLoading = false
        this.messageList.push({ type: 'answer', text: data.data })
      }
    },

    // ==================== HTTP API 相关 ====================
    
    async sendQuestionViaHttp(question) {
      this.isLoading = true
      this.currentQuestion = question
      this.messageList.push({ type: 'question', text: question })
      
      try {
        // 直接调用chatbot API获取回答
        const response = await axios.get('http://localhost:1090/chatbot/api/v1.0/get', {
          params: { question: question },
          timeout: 30000
        })
        
        console.log('API响应:', response.data)
        this.currentAnswer = response.data
        this.isLoading = false
        this.messageList.push({ type: 'answer', text: response.data })
        
      } catch (error) {
        console.error('请求失败:', error)
        this.isLoading = false
        this.currentAnswer = '抱歉，网络连接出现问题，请稍后再试。'
        this.messageList.push({ type: 'error', text: '网络连接失败' })
      }
    },

    // ==================== 界面交互 ====================
    
    questionnaire(event, index) {
      this.currentQuestion = event.target.innerHTML
      document.getElementById('question').innerHTML = event.target.innerHTML
    },
    
    // 确认按钮 - 发送问题
    handleSubmit() {
      const questionEl = document.getElementById('question')
      const question = questionEl.textContent || questionEl.innerHTML
      
      if (!question || question.trim() === '') {
        console.log('问题为空，不发送')
        return
      }
      
      console.log('发送问题:', question)
      
      // 使用HTTP API发送（更可靠）
      this.sendQuestionViaHttp(question)
    },

    // 语音播报
    speak(text) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'zh-CN'
      utterance.volume = 1
      utterance.rate = 1
      utterance.pitch = 1
      window.speechSynthesis.speak(utterance)
    },
    
    // 播报当前回答
    speakCurrentAnswer() {
      if (this.currentAnswer) {
        this.speak(this.currentAnswer)
      }
    },
    translation () {
      if (this.state === 0) {
        //console.log(this.count);
        this.translationStart()
        this.state = 1
        this.statename = '结束录音'
      }
      else {
        this.translationEnd()
        this.state = 0
        this.statename = '开始录音'
      }
    },
    translationStart(){
      iatRecorder.start()
      this.timerId = setTimeout(() => {
        this.state = 0
        this.statename = '开始录音'
        this.translationEnd();
      }, 30000);
    },
    translationEnd () {
      clearTimeout(this.timerId);
      iatRecorder.onTextChange = function(text){
        console.log(text)
        let inputText = text
          this.searchData= inputText.substring(0, inputText.length - 1);//文字处理，因为不知道为什么识别输出的后面都带‘。’，这个方法是去除字符串最后一位
      }
      iatRecorder.stop()
      let ask = document.querySelector('#question')
      ask.textContent = iatRecorder.resultText;
    }


  },
  mounted(){
    console.log('ChatView已挂载')
    console.log('WebSocket地址:', WS_ADDRESS)
  },
  beforeUnmount() {
    if (this.webSocketObject) {
      this.webSocketObject.close()
    }
  }
}
</script>

<template>
  <div class="top">
    <img src="./logo.png" class="pic">
    <span class="name">文渊问答助手</span>
  </div>
  <div class="chat">
    <div class="answer">
      <img src="./logo.png">
      <div class="answer_content">{{ currentAnswer }}</div>
      <img src="./logo3.png" @click="speakCurrentAnswer()" style="width: 20px; height: 20px; position: absolute; left: 520px; top: 20px; cursor: pointer;" title="语音播报">
    </div>
    <div class="right">
      <img src="./logo1.png" class="logo1">
      <div id="question" class="ask">{{ currentQuestion }}</div>
      <button class="submit" @click="handleSubmit()" :disabled="isLoading">{{ isLoading ? '获取中...' : '确认' }}</button>
    </div>
    <div class="answer1">
      <div v-for="(item, index) in messageList" :key="index" class="message-item">
        <div v-if="item.type === 'question'" class="user-msg">问：{{ item.text }}</div>
        <div v-else-if="item.type === 'answer'" class="bot-msg">
          答：{{ item.text }}
          <button @click="speak(item.text)" class="speak-btn">播报</button>
        </div>
        <div v-else class="error-msg" style="color: red;">{{ item.text }}</div>
      </div>
    </div>
    <div>
      <img src="./logo2.png" @click="translation" style="width:80px;height: 80px;position:absolute;left:50%;top:80%;cursor:pointer;"> 
      <span class="state">{{ statename }}</span>
    </div>
  </div>
  <div class="ques">
    <h1 class="text1">您可能想问：</h1>
    <h2 class="text1">（点击使用预设问题）</h2>
    <button v-for="(item, index) in items" :key="index" @click="questionnaire($event, index)" :id="`btn-${index}`" style="padding: 10px 10px;margin: 10px 20px 3px 3px; font-size: 20px; cursor: pointer;">
      {{item.message}}
    </button>
  </div>
</template>

<style>
.top{
  position: absolute;
  left: 0px;
  top: 0px;
  width: 1440px;
  height: 20%;
  border-radius: 6px 6px 0px 0px;
  opacity: 1;
  background: #FAFBFF;
}
.pic{
  width:80px;
  height: 80px;
  position:absolute;
  left:30px;
  top:20px;
}
.name{
  position: absolute;
  left: 150px;
  top: 40px;
  opacity: 1;
	color: #0D1C2E;
  font-family: Alimama DongFangDaKai;
  font-size: 36px;
  font-weight: normal;
  line-height: 25px;
  text-align: center;
  display: flex;
  align-items: center;
  letter-spacing: 0px;
	font-variation-settings: "opsz" auto;
}
.chat{
  position: absolute;
  left: 0px;
  top: 120px;
  width: 66.67%;
  height: 80%;
  opacity: 1;
  /* background-color: #e4f4fc; */
  background: linear-gradient(180deg, hwb(199 87% 5%) -13%, #e0e4fc 110%, #d4e4fc 110%);
  background-blend-mode: overlay;
  backdrop-filter: blur(92px);
  /* box-shadow: 0px 12px 50px -12px rgba(0, 0, 0, 0.25),inset -2px 0px 0px 1px rgba(255, 219, 98, 0.45),inset 0px 0px 0px 1px rgba(255, 255, 255, 0.3); */
}
.ques{
  position: absolute;
  left: 66.67%;
  top: 120px;
  width: 33.33%;
  height: 80%;
  opacity: 1;
  background: linear-gradient(180deg, #d8ecfc -13%, #b8d8f4 110%, #b4ccf4 110%);
  background-blend-mode: overlay;
  padding:10px 10px; 
}
.question_buttom{
  font-size: 50px;
  width: 100px;
}
.ask{
  padding: 10px 10px 10px 10px;
  position: absolute;
  left: 10px;
  top: 200px;
  width: 350px;
  opacity: 1;
  box-sizing: border-box;
  border: 1px solid rgba(112, 124, 151, 0.25);
  box-shadow: 10px 10px 25px 0px rgba(112, 124, 151, 0.05),15px 15px 35px 0px rgba(112, 124, 151, 0.05),10px 10px 50px 0px rgba(112, 124, 151, 0.03);
  font-family: Alibaba PuHuiTi 3.0;
  font-size: 20px;
  font-weight: 600;
    /* line-height: 26px; */
}

.right{
  position: absolute;
  right: 60%;
}
.answer{
  position: absolute;
  left: 88px;
  top: 27px;
  width: 400px;
  height: 50.6px;
  opacity: 1;
  font-family: Alibaba PuHuiTi 2.0;
  font-size: 20px;
  font-weight: 600;
  line-height: 26px;
  letter-spacing: 0px;
  color: hsl(0, 100%, 2%);
}
.logo1{
  width:65px;
  height: 65px;
  position:absolute;
  left:400px;
  top:27px;
}
.answer1{
  position: absolute;
  left: 88px;
  top: 130px;
  width: 400px;
  height: 50.6px;
  opacity: 1;
  font-family: Alibaba PuHuiTi 2.0;
  font-size: 20px;
  font-weight: 600;
  line-height: 26px;
  letter-spacing: 0px;
  color: hsl(0, 100%, 2%);
}
.answer_content{
  position: absolute;
  left: 100px;
  top: 20px;
  width: 400px;
  padding: 10px 10px 10px 10px;
  border-radius: 0px 10px 10px 10px;
  opacity: 1;
  background: linear-gradient(96deg, #60A9F6 9%, #2A8BF2 99%);
/* 外部/Shadow Block Message My Opponent */
  box-shadow: 10px 10px 25px 0px rgba(42, 139, 242, 0.1),15px 15px 35px 0px rgba(42, 139, 242, 0.05),10px 10px 50px 0px rgba(42, 139, 242, 0.1);
}
.meeting{
  padding: 10px 10px 10px 10px;
  position: absolute;
  left: 400px;
  top: 200px;
  width: 350px;
  height: 200px;
  overflow-y: auto;
  opacity: 1;
  font-family: Alibaba PuHuiTi 3.0;
  font-size: 20px;
  font-weight: 600;
}
.state{
  padding: 10px 10px 10px 10px;
  position: absolute;
  left: 465px;
  top: 580px;
  width: 350px;
  height: 150px;
  overflow-y: auto;
  opacity: 1;
  font-family: Alibaba PuHuiTi 3.0;
  font-size: 20px;
  font-weight: 600;
}

.submit{
  position: absolute;
  left: 380px;
  top: 180px;
  width: 80px;
  height: 50.6px;
  opacity: 1;
  font-family: Alibaba PuHuiTi 2.0;
  font-size: 20px;
  line-height: 26px;
  letter-spacing: 0px;
  color: hsl(0, 100%, 2%);
  border-color: #767d86;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit:hover {
  background-color: #4a90d9;
  color: white;
}

.submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #ccc;
}

/* 消息列表样式 */
.message-item {
  margin: 8px 0;
  padding: 8px;
}

.user-msg {
  background-color: #e8f4ff;
  padding: 10px;
  border-radius: 8px;
  text-align: right;
}

.bot-msg {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 8px;
  text-align: left;
}

.speak-btn {
  margin-left: 10px;
  padding: 2px 8px;
  font-size: 12px;
  cursor: pointer;
  background-color: #60A9F6;
  color: white;
  border: none;
  border-radius: 4px;
}

.error-msg {
  padding: 10px;
  border-radius: 8px;
  background-color: #ffe0e0;
}
</style>