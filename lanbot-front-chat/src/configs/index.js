// 后端服务器地址配置
// Docker环境使用环境变量，本地开发使用默认值

const WS_PORT = import.meta.env.VITE_WS_PORT || '20551';  // 边缘服务器WebSocket端口
const API_PORT = import.meta.env.VITE_API_PORT || '20550';  // 边缘服务器HTTP端口

const WS_ADDRESS = `ws://localhost:${WS_PORT}`;
const API_ADDRESS = `http://localhost:${API_PORT}`;

// chatbot直接API地址（可选）
const CHATBOT_API = `http://localhost:1090/chatbot/api/v1.0/get`;

export { WS_ADDRESS, API_ADDRESS, CHATBOT_API };
export default WS_ADDRESS;