class Error(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, msg, status_code=403):
        self.status_code = status_code
        super().__init__(msg)


class ForbiddenError(Error):
    """
    禁止访问
    """


class ResourceError(Error):
    """
    资源获取错误
    """


class DBError(Error):
    """
    数据库相关错误
    """


class ParamError(Error):
    """
    参数类型错误
    """


class ResponseError(Error):
    """
    响应错误
    """
