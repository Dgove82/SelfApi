from src.library.decorator import allow
from api.model.files import Files
from src.library.model import SQLServer
from src.utils.make_sql import QueryBuild
from src.library.controller import BaseCtrl
from src.library.error import ForbiddenError


class FilesCtrl(BaseCtrl):
    def __init__(self):
        super().__init__()
        self.model = Files

    @allow('POST')
    async def upload(self, request):
        # print(await request.form())
        return 'ok'

    # @allow('POST')
    # async def add(self, request):
    #     raise ForbiddenError(f'该资源不允许使用该方法，建议使用/upload')
