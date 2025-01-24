from pathlib import Path
import atexit

BASE_DIR = Path(__file__).resolve().parent

DEBUG = True


class SQLConfig:
    ENGINE = 'mysql+pymysql'
    HOST = 'localhost'
    PORT = 3306
    USER = 'dgove'
    PASSWORD = '123'
    DB = 'experial'


CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = []

# 允许的请求方法
CORS_ALLOW_METHODS = (
    'GET'
)

# 允许的请求头
CORS_ALLOW_HEADERS = ()

# CORS最大有效时间
CORS_MAX_AGE = 10

MIDDLEWARES = [
    'src.library.middleware.BaseMiddleware',
]

from settings import *

if "LOG_FILE" not in dir():
    LOG_FILE = f'{TimeTool.get_format_day()}.log'
    log = LogTool(log_level="DEBUG", log_file=LOG_FILE, project_root=BASE_DIR, is_debug=DEBUG)
