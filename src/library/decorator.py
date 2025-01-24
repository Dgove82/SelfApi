from src.library.error import ForbiddenError


def allow(method: str):
    # method: 请求方法
    def decorator(func):
        def method_allow(*args, **kwargs):
            if len(args) > 1:
                request = args[1]
                if request.method != method:
                    raise ForbiddenError('请求错误')
            return func(*args, **kwargs)

        return method_allow

    return decorator
