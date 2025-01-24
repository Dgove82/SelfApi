# class BaseParam:
#
#     def struct_dict(self, filterate=True):
#         attrs = vars(self)
#         if filterate:
#             return {k: v for k, v in attrs.items() if v is not None}
#         else:
#             return attrs
#
#
# class ParamStruct(BaseParam):
#     def __init__(self, base=None, join=None, where=None, group=None, having=None, order=None, limit=None, offset=None,
#                  keys=None, values=None):
#         self.base: dict = base
#         self.join: list = join if join else []
#         self.where: dict = where
#         self.group: list = group if group else []
#         self.having: dict = having
#         self.order: list = order if order else []
#         self.limit: int = limit
#         self.offset: int = offset
#         self.keys: list = keys if keys else []
#         self.values: dict = values
#
#
# p = ParamStruct()
# print(p.struct_dict())

# import importlib
# from src.conf import MIDDLEWARES
#
#
# async def run_middlewares():
#     for m in MIDDLEWARES:
#         parts = m.split('.')
#         module_name = '.'.join(parts[:-1])
#         class_name = parts[-1]
#
#         # 动态导入模块
#         module = importlib.import_module(module_name)
#
#         # 获取类
#         cls = getattr(module, class_name)
#
#         # 创建类的实例
#         instance = cls()
#
#         # 调用实例的异步方法
#         await instance.before_request(1)
#
#
# # 假设您在一个异步环境中运行此代码，例如在 asyncio 事件循环中
# import asyncio
#
# # 启动事件循环并运行 run_middlewares 函数
# asyncio.run(run_middlewares())
# def ttt():
#     try:
#         print('ok')
#         return
#     except Exception as e:
#         print('no')
#     finally:
#         print('end')


# 写个装饰器
def decrote(qs):
    def wrapper(cls):
        # 修改类的__init__方法来添加属性
        original_init = cls.__init__

        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self.new_attr = qs  # 添加新属性

        cls.__init__ = new_init
        return cls
    return wrapper



@decrote('look')
class CT:
    def tt(self):
        print('in')


a = CT()
a.tt()
print(a.new_attr)
