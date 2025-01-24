from src.library.decorator import allow


class HelloCtrl:

    @allow('GET')
    async def index(self, request, s):
        return {'status': 'success', 'msg': 'Hello World!', 'data': None}
