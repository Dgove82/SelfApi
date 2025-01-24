import importlib
import os
from fastapi import Response, Request

from src import conf
from src.library.error import ResourceError
from src.utils.tools import ContentTool


class RequestHandler:
    def __init__(self, request: Request):
        self.request = request

    def _vote_res(self, res):
        if isinstance(res, Response):
            return res
        elif isinstance(res, Request):
            self.request = res

    @staticmethod
    def instantiate_middleware(middleware: str):
        """
        实例化中间件
        """
        parts = middleware.split('.')
        module_name = '.'.join(parts[:-1])
        class_name = parts[-1]
        try:
            module = importlib.import_module(module_name)
            return getattr(module, class_name)()
        except Exception as e:
            raise ResourceError(f'中间件异常: {e}')

    async def _request(self):
        """
        [分派路由前]请求中间件操作
        """
        for middleware in conf.MIDDLEWARES:
            ware = self.instantiate_middleware(middleware)
            if hasattr(ware, 'before_request'):
                res = await ware.before_request(self.request)
                self._vote_res(res)

        for middleware in conf.MIDDLEWARES:
            ware = self.instantiate_middleware(middleware)
            if hasattr(ware, 'after_request'):
                res = await ware.after_request(self.request)
                self._vote_res(res)

    async def _router_distribute(self):
        """
        路由分派
        :return: str | dict | list
        """

        module = self.request.path_params.get('module', "")
        resource = self.request.path_params.get('resource', "")
        action = self.request.path_params.get('action', "")

        try:
            entries = os.listdir(f'{conf.BASE_DIR}/{module}/controller/')
        except FileNotFoundError:
            raise ResourceError('Module does not exist.')

        interfaces = [f[:-3] for f in entries if f.endswith('.py')]
        interface_name = resource.replace('-', '_')
        if resource not in interfaces:
            raise ResourceError('Resource does not exist.', status_code=404)

        ctrl_module = importlib.import_module(f'{module}.controller.{interface_name}')
        ctrl_name = ContentTool(interface_name).multiword_construct(delimiter='_')
        ctrl_class = getattr(ctrl_module, f'{ctrl_name}Ctrl')
        instance = ctrl_class()
        if hasattr(instance, action) and callable(getattr(instance, action)):
            if getattr(instance, action).__name__ == 'method_allow':
                res = await getattr(instance, action)(self.request)
                if isinstance(res, dict):
                    res['action'] = action
                return res
            else:
                raise ResourceError('Action does not allow.', status_code=405)
        else:
            raise ResourceError('Action does not exist.', status_code=405)

    async def _response(self, response) -> Response:
        """
        [反馈-构造完响应]响应中间件操作
        """
        for middleware in conf.MIDDLEWARES:
            ware = self.instantiate_middleware(middleware)
            if hasattr(ware, 'before_resposne'):
                response = await ware.before_resposne(self.request, response)

        for middleware in conf.MIDDLEWARES:
            ware = self.instantiate_middleware(middleware)
            if hasattr(ware, 'after_response'):
                response = await ware.after_response(self.request, response)

        return response

    async def _exception(self, error):
        """
        异常中间件操作
        """
        for middleware in conf.MIDDLEWARES:
            ware = self.instantiate_middleware(middleware)
            if hasattr(ware, 'deal_exception'):
                res = await ware.deal_exception(error)
                if res:
                    return res

    async def handler(self):
        """
        处理中心
        """
        try:
            res = await self._request()
            if isinstance(res, Response):
                res = await self._response(res)
                return res
            res = await self._router_distribute()
        except Exception as e:
            res = await self._exception(e)

        res = await self._response(res)
        return res
