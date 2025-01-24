import time

from src.library.decorator import allow
from src.library.error import ParamError
from src.utils.make_sql import Query
from src.library.model import SQLServer
from src.utils.make_sql import QueryBuild
from src.utils.tools import DataHandler


class BaseCtrl:
    def __init__(self):
        self.model = None
        self.query = Query
        self.params = None

    @staticmethod
    def check_type(form, val):
        forms = {"int": "整数", "float": "浮点数", "str": "字符串", "list": "列表", "tuple": "元组", "dict": "字典"}
        try:
            temp = eval(f"{form}({val})")
            return temp
        except Exception:
            raise ParamError(f"参数为{forms.get(form)}")

    def wrap_params(self):
        self.params.base.table = self.model.get_table_name()
        self.params = self.params.build()
        return self.params

    def execute_params(self, params: dict):
        params.update(self.wrap_params())
        sql = QueryBuild(params).build().sql
        res = SQLServer().execute(sql)
        return res

    def before_key(self, request):
        self.params = self.query()
        self.params.base.way = 'select'
        self.params.where = request.params
        return {}

    @allow("GET")
    async def key(self, request):
        params = self.before_key(request)
        return self.execute_params(params)

    def start_all(self, request):
        self.params = self.query()
        self.params.base.way = 'select'

        params = request.params
        self.params.offset = self.check_type("int", params.get("offset", 0))
        self.params.limit = self.check_type("int", params.get("limit", 10))
        return params

    @allow('GET')
    async def all(self, request):
        params = self.start_all(request)
        return self.execute_params(params)

    def start_add(self, request):
        self.params = self.query()
        self.params.base.way = 'insert'
        params: dict = request.data
        if "values" not in params.keys():
            raise ParamError("缺少关键参数")

        now = int(time.time())
        params["values"].update({"ctime": now, "utime": now, "status": 1})
        return params

    @allow('POST')
    async def add(self, request):
        params = self.start_add(request)
        return self.execute_params(params)

    def start_update(self, request):
        self.params = self.query()
        self.params.base.way = 'update'
        params: dict = request.data
        if not DataHandler.check_keys(params, ["where", "values"]):
            raise ParamError("缺少关键参数")
        now = int(time.time())
        params['values'] = DataHandler.filter_data(params["values"], ["cname", "ctime", "status"])
        params["values"].update({"utime": now})
        return params

    @allow('PUT')
    async def update(self, request):
        params = self.start_update(request)
        return self.execute_params(params)

    def start_delete(self, request):
        self.params = self.query()
        self.params.base.way = 'update'
        params: dict = request.data
        if not DataHandler.check_keys(params, ["where", "values"]):
            raise ParamError("缺少关键参数")
        now = int(time.time())
        params['values'] = {"utime": now, "status": 0}
        return params

    @allow('DELETE')
    async def delete(self, request):
        params = self.start_delete(request)
        return self.execute_params(params)

