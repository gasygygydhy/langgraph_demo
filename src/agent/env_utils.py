import os

from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY')


MINIMAX_BASE_URL = os.getenv('MINIMAX_BASE_URL')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL')

LOCAL_BASE_URL = os.getenv('LOCAL_BASE_URL')

#千问
QW_API_KEY = os.getenv('QW_API_KEY')
QW_BASE_URL = os.getenv('QW_BASE_URL')
DB_URI = os.getenv('DB_URI')
