from sqlalchemy.orm import declarative_base
from src.utils.make_sql import QueryBuild
import re
from typing import Union

from sqlalchemy import create_engine, text, delete
from sqlalchemy.orm import sessionmaker
from settings import SQLConfig
from src.library.error import DBError
from src.conf import log

Base = declarative_base()


class ModelBase(Base):
    __abstract__ = True

    def __init__(self):
        super().__init__()
        self.params = ParamStruct()

    @classmethod
    def get_table_name(cls):
        """
        获取表名
        """
        return cls.__tablename__

    @classmethod
    def get_primary_key(cls):
        """
        获取主键字段名称
        """
        # 直接访问 __table__.primary_key 来获取主键字段
        primary_key_columns = cls.__table__.primary_key.columns
        # 返回主键字段的名称列表
        return list(primary_key_columns.keys())

    @classmethod
    def get_columns(cls):
        """
        获取所有字段
        """
        return cls.__table__.columns.keys()

    def read_attr_value(self, attr_name):
        """
        根据模属性获取值
        """
        return getattr(self, attr_name, None)

    def read_attr(self):
        """
        获取所有模型中字段所有值
        """
        return {attr: self.read_attr_value(attr) for attr in self.get_columns()}

    def deal_param_base(self, way='select'):
        self.params.base = ParamBase(table=self.get_table_name(), way=way).struct_dict()

    def deal_param_values(self):
        self.params.values = self.read_attr()


class BaseParam:

    def struct_dict(self, filterate=True):
        attrs = vars(self)
        if filterate:
            return {k: v for k, v in attrs.items() if v is not None}
        else:
            return attrs


class ParamStruct(BaseParam):
    def __init__(self, base=None, join=None, where=None, group=None, having=None, order=None, limit=None, offset=None,
                 keys=None, values=None):
        self.base: dict = base
        self.join: list = join if join else []
        self.where: dict = where
        self.group: list = group if group else []
        self.having: dict = having
        self.order: list = order if order else []
        self.limit: int = limit
        self.offset: int = offset
        self.keys: list = keys if keys else []
        self.values: dict = values


class ParamBase(BaseParam):
    """
    'base': {
            'table': 'user',
            'alias': 'us',
            'way': 'select'
        }
    """

    def __init__(self, table=None, alias=None, way=None):
        self.table: str = table
        self.alias: str = alias
        self.way: str = way


class ParamJoin(BaseParam):
    """
    {
        'table': 'orders',  # 表名
        'alias': 'o',  # 别名
        'style': 'INNER',  # 连接方式
        'on': {  # 连接条件
            'o.id': 'us.id'
        }
    }
    """

    def __init__(self, table=None, alias=None, style=None, on=None):
        self.table = table
        self.alias = alias
        self.style = style
        self.on = on


class SQLServer:
    DATABASE_URL = f'{SQLConfig.ENGINE}://{SQLConfig.USER}:{SQLConfig.PASSWORD}@{SQLConfig.HOST}:{SQLConfig.PORT}/{SQLConfig.DB}'
    SESSION = sessionmaker(autocommit=False, autoflush=True, bind=create_engine(DATABASE_URL))

    @staticmethod
    def get_session():
        session = SQLServer.SESSION()
        try:
            yield session
        finally:
            session.close()

    @staticmethod
    def get_db():
        return next(SQLServer.get_session())

    def execute(self, sql: str) -> list:
        """
        :param sql: sql语句
        :return result_dict: 执行结果
        """
        statement = text(sql)
        log.info(f'即将执行<{statement}>sql命令')
        if re.match(r'^select', sql, re.IGNORECASE) is not None:
            res_dict_list = self.select_by_sql(statement)
            log.info(f'查询结果: {res_dict_list}')
            return res_dict_list
        elif re.match(r'^insert', sql, re.IGNORECASE) is not None:
            res = self.insert_by_sql(statement)
            log.info(f'插入的数据: {res}')
            return res
        elif re.match(r'^update', sql, re.IGNORECASE) is not None:
            res = self.update_by_sql(statement)
            log.info(f'更新的数据: {res}')
            return res
        elif re.match(r'^delete', sql, re.IGNORECASE) is not None:
            res = self.delete_real_by_sql(statement)
            log.info(f'删除的数据: {res}')
            return res
        else:
            log.error(f'sql命令错误: 无对应操作')
            raise DBError('无对应操作方法')

    def select_by_sql(self, statement) -> list:
        session = self.get_db()

        cursor = session.execute(statement)
        result_tuples = cursor.fetchall()
        column_names = cursor.keys()
        result_dict_list = [dict(zip(column_names, row)) for row in result_tuples]
        # print(result_dict)

        cursor.close()
        session.close()
        return result_dict_list

    def select_last_update(self, table):
        """
        获取最新更新的记录
        """
        sql = f'select * from {table} order by utime desc limit 1'
        return self.execute(sql)

    def sql_operation(self, statement, table):
        """
        执行更新操作
        """
        session = self.get_db()
        try:
            res = session.execute(statement)
            log.info(f'操作了{res.rowcount}条记录')
            session.commit()
            return self.select_last_update(table)
        except Exception as e:
            log.error(f'数据库执行异常: {e}')
            session.rollback()
            raise DBError('数据库执行异常')
        finally:
            session.close()

    def insert_by_sql(self, statement):
        table = re.findall(r'into `(.*?)`', str(statement), re.IGNORECASE)[0]
        return self.sql_operation(statement, table)

    def update_by_sql(self, statement):
        table = re.findall(r'update `(.*?)`', str(statement), re.IGNORECASE)[0]
        return self.sql_operation(statement, table)

    def delete_real_by_sql(self, statement):
        sql = re.sub(r'delete|DELETE', 'select *', str(statement))
        # 将被真删的数据
        op_target = self.execute(sql)
        session = self.get_db()
        try:
            session.execute(statement)
            session.commit()
            return op_target
        except Exception as e:
            log.error(f'数据库执行异常: {e}')
            session.rollback()
            raise DBError('数据库执行异常')
        finally:
            session.close()

    def mock_delete_by_sql(self, statement):
        sql = re.sub(r'delete|DELETE ', 'update', str(statement))
        sql = re.sub(r'from|FROM', '', sql)
        if not re.match(r'[\S\s]*where[\S\s]*', sql, re.IGNORECASE):
            raise DBError('删除必须要有where')
        sql = re.sub(r'where|WHERE', 'set status = 0 where', sql)
        return self.update_by_sql(sql)

    def insert_model(self, data: Union[list, ModelBase]):
        session = self.get_db()
        try:
            if isinstance(data, list):
                session.add_all(data)
            elif isinstance(data, ModelBase):
                session.add(data)
            else:
                raise TypeError
            session.commit()
        except Exception as err:
            session.rollback()
            log.error(f'插入失败,原因:{err}')
        finally:
            session.close()

    def delete_model(self, model):
        """
        清空数据表
        :param model:
        :return:
        """
        delete_statement = delete(model)
        session = self.get_db()
        try:
            session.execute(delete_statement)
            session.commit()
            log.success(f'{model.__tablename__}数据表已清空')
        except Exception as err:
            session.rollback()
            log.error(f"清空{model.__tablename__}表时发生错误: {err}")
        finally:
            session.close()

    def update_instance(self, instance):
        session = self.get_db()
        session.add(instance)
        session.commit()
        session.close()

    def model_is_exist(self, model):
        session = self.get_db()
        flag = session.query(model).first()
        return True if flag is not None else False
