import json
from fastapi import Request, Response
from src import conf
from src.utils.tools import DataHandler
import traceback
from json import dumps


class BaseMiddleware:
    async def before_request(self, request: Request):
        scope = request.scope
        conf.log.info(
            f'REQUEST {scope.get("type", None).upper()}/{scope.get("http_version", None)} '
            f'{scope.get("method", None).upper()} {scope.get("server", None)} FROM {scope.get("client", None)} '
            f'FOR {scope.get("path", None)}?{scope.get("query_string", b"").decode()}')
        return request

    async def after_request(self, request: Request):
        forbidden_param = ['base']
        params = dict(request.query_params)
        request.params = DataHandler.filter_data(params, forbidden_param)
        # print(request.params)

        data = await request.form()
        request.data = DataHandler.filter_data(dict(data), forbidden_param)
        # print(request.data)
        return request

    async def before_resposne(self, request, response: Response):
        return response

    async def after_response(self, request, response: Response):
        scope = request.scope
        info = (f'RESPONSE {response.status_code} {scope.get("type", None).upper()}/{scope.get("http_version", None)} '
                f'{scope.get("method", None).upper()} {scope.get("server", None)} FROM {scope.get("client", None)} '
                f'FOR {scope.get("path", None)}?{scope.get("query_string", b"").decode()}')
        if response.status_code != 200:
            conf.log.warning(info)
        else:
            conf.log.info(info)
        return response

    async def deal_exception(self, exc):
        conf.log.error('构造响应体时遇到异常')
        conf.log.error(traceback.format_exc())
        status_code = exc.status_code
        content = json.dumps({'status': 'error', 'msg': str(exc)})
        return Response(content=content, status_code=status_code)


class CorsMiddleware:
    async def before_request(self, request):
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Methods': ','.join(conf.CORS_ALLOW_METHODS),
                'Access-Control-Allow-Headers': ','.join(conf.CORS_ALLOW_HEADERS),
                'Access-Control-Max-Age': conf.CORS_MAX_AGE,
            }
            return Response(content='Pre inspection passed', headers=headers)

    async def after_request(self, request):
        pass

    async def before_resposne(self, request, response):
        if isinstance(response, Response):
            return response

        headers = {}
        if isinstance(response, (dict, list)):
            response = dumps(response, sort_keys=True)
            headers['Content-Type'] = 'application/json'
        else:
            headers['Content-Type'] = 'text/plain'
        return Response(content=response, headers=headers)

    async def after_response(self, request, response):
        # CORS跨域
        if conf.CORS_ORIGIN_ALLOW_ALL:
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        origin = request.headers.get('Origin', None)
        if origin in conf.CORS_ORIGIN_WHITELIST:
            response.headers['Access-Control-Allow-Origin'] = origin
        return response
