import os.path
from loguru import logger
import time
import sys
import re
import hashlib
import json
import inspect

class DataHandler:
    @staticmethod
    def filter_data(items: dict, forbidden: list):
        temp = {}
        for item in items:
            value = items.get(item)
            if item in forbidden:
                continue
            try:
                value = json.loads(value)
            except Exception:
                pass
            finally:
                temp.update({item: value})
        return temp

    @staticmethod
    def check_keys(items: dict, keys: list):
        contain_keys = items.keys()
        for key in keys:
            if key not in contain_keys:
                return False
        return True


class ContentTool:
    def __init__(self, content: str):
        self.content = content

    def json_parse(self):
        """
        json字符串转python对象
        """
        try:
            res = json.loads(self.content)
        except json.decoder.JSONDecodeError:
            res = self.content
        return res

    def byte_decode_md5(self):
        """
        字节流转md5
        """
        return hashlib.md5(self.content.encode()).hexdigest()

    @staticmethod
    def first_upper(s: str) -> str:
        """
        首字母大写
        """
        return s[0].upper() + s[1:]

    def multiword_construct(self, delimiter='_') -> str:
        """
        多单词构造首单词大写
        """
        return ''.join(list(map(lambda s: self.first_upper(s), self.content.split(delimiter))))


class FileTool:
    def __init__(self, path):
        self.path = str(path)
        self.dir = None
        self.name = None

    @staticmethod
    def check_path(path):
        if not os.path.exists(path):
            os.makedirs(path)

    def parse_path(self):
        eles = self.path.split('/')
        if re.match(r'.*?\.\w+', eles[-1]):
            self.name = eles[-1]
            self.dir = '/'.join(eles[:-1])
        else:
            self.dir = self.path

    def create_file(self):
        with open(self.path, 'w'):
            pass

    def is_exists(self):
        return os.path.exists(self.path)

    def exists(self):
        """
        确保文件/目录存在
        :return:
        """
        self.parse_path()
        if os.path.exists(self.path):
            return True
        else:
            os.makedirs(self.dir, exist_ok=True)
            self.create_file()
            return True

    def write(self, data):
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(data)


class TimeTool:
    @staticmethod
    def now():
        return time.localtime()

    @staticmethod
    def nowstamp():
        return int(time.time())

    @staticmethod
    def get_format_time():
        return time.strftime("%Y-%m-%d_%H-%M-%S", TimeTool.now())

    @staticmethod
    def get_format_day():
        return time.strftime("%Y-%m-%d", TimeTool.now())

    @staticmethod
    def strftime_for_format(timestamp, format_type='%Y-%m-%d %H:%M:%S'):
        return time.strftime(format_type, time.localtime(timestamp))


class LogTool:
    def __init__(self, log_level="DEBUG", log_file="temp.log", project_root='', is_debug=False):
        self.log_level = log_level
        self.log_file = log_file
        self.is_debug = is_debug
        # 项目根目录
        self.project_root = project_root
        self.logger = logger
        self.configure_logging()
        self.last_info = None

    def capture_msg(self, message):
        self.last_info = message.format()

    def configure_logging(self):
        # 配置日志格式和输出
        self.logger.remove()  # 清除默认的日志处理器
        color_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " \
                       "<cyan>{extra[prefix]}</cyan> | " \
                       "<level>{level}</level> | " \
                       "<level>{message}</level>"
        self.logger.add(
            sink=self.log_file,
            level=self.log_level,
            format=color_format,
            rotation="500 MB",  # 日志文件轮转，每个文件最大500MB
            retention="1 days",  # 保留最近10天的日志
            enqueue=True,  # 异步写入日志
            backtrace=True,  # 记录堆栈跟踪
            diagnose=True,  # 记录异常诊断信息
        )
        if self.is_debug:
            self.logger.add(sys.stdout, level=self.log_level, backtrace=True, format=color_format)
        self.logger.add(self.capture_msg, format=color_format)

    def prefix_info(self):
        frame = inspect.stack()[3]
        file_path = os.path.splitext(os.path.relpath(frame.filename, self.project_root))[0]
        prefix = f"{file_path}{'.' + frame.function if frame.function != '<module>' else ''}:{frame.lineno} "
        return prefix

    def msg_struct(self, level: str, msg: str):
        prefix = self.prefix_info()
        msg = msg.replace('{', '【').replace('}', '】')
        log_method = getattr(self.logger, level.lower())
        log_method(msg, prefix=prefix)
        return self.last_info

    def info(self, msg):
        return self.msg_struct(level="INFO", msg=msg)

    def debug(self, msg):
        return self.msg_struct(level="DEBUG", msg=msg)

    def warning(self, msg):
        return self.msg_struct(level="WARNING", msg=msg)

    def error(self, msg):
        return self.msg_struct(level="ERROR", msg=msg)

    def success(self, msg):
        return self.msg_struct(level="SUCCESS", msg=msg)

    def critical(self, msg):
        return self.msg_struct(level="CRITICAL", msg=msg)

    def exception(self, msg):
        return self.msg_struct(level="EXCEPTION", msg=msg)
