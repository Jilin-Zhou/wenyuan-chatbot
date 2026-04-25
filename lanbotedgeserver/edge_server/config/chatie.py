from config import conf
from dotenv import load_dotenv, find_dotenv

load_dotenv(verbose=True,override=True)

API_URL = conf.get_env_default("CHATIE_API_URL","http://127.0.0.1:1090/chatbot/api/v1.0/get")
CHAT_CONF_NAME = conf.get_env_default("CHAT_CONF_NAME","default")