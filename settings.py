from pathlib import Path
import os
from src.utils.tools import LogTool, FileTool, TimeTool

# 项目目录
BASE_DIR = Path(__file__).resolve().parent

# 是否调试状态
DEBUG = True

URL_RUN = 'http://127.0.0.1:8000'


class SQLConfig:
    ENGINE = 'mysql+pymysql'
    HOST = 'localhost'
    PORT = 3306
    USER = 'dgove'
    PASSWORD = '123'
    DB = 'experial'


# 解除限制
CORS_ORIGIN_ALLOW_ALL = False

# 允许访问的跨域白名单
CORS_ORIGIN_WHITELIST = [
    "http://localhost:63343",
]

# 允许的请求方法
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',  # 更新数据 （局部）
    'POST',
    'PUT',  # 更新数据（全部）
    "TRACE",
    "CONNECT",
    "HEAD"
)

# 允许的请求头
CORS_ALLOW_HEADERS = (
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-requested-with',
)

# CORS最大有效时间
CORS_MAX_AGE = 86400

MIDDLEWARES = [
    'src.library.middleware.CorsMiddleware',
    'src.library.middleware.BaseMiddleware',
]

LOG_PATH = os.path.join(BASE_DIR, 'logs')
FileTool.check_path(LOG_PATH)
LOG_FILE = f'{os.path.join(LOG_PATH, TimeTool.get_format_day())}.log'
log = LogTool(log_level="DEBUG", log_file=LOG_FILE, project_root=BASE_DIR, is_debug=DEBUG)
