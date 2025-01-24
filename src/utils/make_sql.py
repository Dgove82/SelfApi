"""
file: make_sql.py
author: dgove
date: 2024.6.20
description: Edit SQL statements based on the dictionary

param example:
    params = {
        # 必要
        'base': {
            'table': 'user',
            'alias': 'us',
            'way': 'select'
        },
        # select 可用
        'join': [
            {
                'table': 'users',  # 表名
                'alias': 'u',  # 别名
                'style': 'LEFT',  # 连接方式
                'on': {  # 连接条件
                    'and': {
                        'u.id': 'us.id',
                        'u.score': 'us.score',
                    },
                }
            },
            {
                'table': 'orders',  # 表名
                'alias': 'o',  # 别名
                'style': 'INNER',  # 连接方式
                'on': {  # 连接条件
                    'o.id': 'us.id'
                }
            }
        ],
        # update/delete/selct 可用
        'where': {  # where条件
            'and': {
                'id': {'neq': 1},  # id不等于1
                'age': {'lt': 30},
                'score': {'gte': 80},
            },
            'or': {
                'id': {'neq': 1},
                'age': {'lt': 30},
            },
            'id': 2
        },
        # select 可用
        'group': ['age', 'score'],
        # select 可用
        'having': {
            'COUNT(id)': {'gte': 5},
            'AVG(score)': {'lt': 90}
        },
        # select 可用
        'order': [('name', 'desc'), 'age'],
        # select 可用
        'limit': 10,
        # select 可用
        'offset': 0,
        # select 可用
        'keys': ['id', 'name'],
        # insert/update 必要
        'values': {
            'age': 30,
            'score': 80,
        }
    }
"""
import re


class Query:
    class Base:
        table = None
        alias = None
        way = None

    def __init__(self):
        self.base = Query.Base()
        self.join = []

        self.where = {}

        self.group = []

        self.order = []

        self.having = {}

        self.limit = None

        self.offset = None

        self.keys = []

        self.values = {}

    def build(self):
        params = {}

        # 检查 Base 属性并添加到 params
        base_params = {}
        if self.base.table is not None:
            base_params['table'] = self.base.table
        if self.base.alias is not None:
            base_params['alias'] = self.base.alias
        if self.base.way is not None:
            base_params['way'] = self.base.way
        if base_params:
            params['base'] = base_params

        # 检查其它属性并添加到 params
        if self.join:
            params['join'] = self.join
        if self.where:
            params['where'] = self.where
        if self.group:
            params['group'] = self.group
        if self.order:
            params['order'] = self.order
        if self.having:
            params['having'] = self.having
        if self.limit is not None:
            params['limit'] = self.limit
        if self.offset is not None:
            params['offset'] = self.offset
        if self.keys:
            params['keys'] = self.keys
        if self.values:
            params['values'] = self.values

        return params


class QueryBuild:
    def __init__(self, param):
        self.param = param
        self.base = None
        self.query = []
        self.sql = None

    @staticmethod
    def decorate_key(keyword):
        r = re.match(r'^(?P<func>[a-zA-Z]*)\((?P<key>.*)\)', keyword)
        if not r:
            temp = keyword.split('.')
            if len(temp) > 1:
                keyword = []
                for t in temp:
                    if t == '*':
                        keyword.append(t)
                    else:
                        keyword.append(f'`{t}`')

                keyword = '.'.join(keyword)
            else:
                keyword = f'`{keyword}`'
        else:
            keyword = f'{r.group("func")}(`{r.group("key")}`)'
        return keyword

    @staticmethod
    def generate_rela(keyword, condition: dict):
        operators = {
            'eq': '=',
            'neq': '<>',
            'lt': '<',
            'lte': '<=',
            'gt': '>',
            'gte': '>=',
            'like': 'LIKE',
            'rlike': 'RLIKE'
        }
        # compare, val = condition.popitem()
        compare, val = condition.copy().popitem()

        if not compare:
            raise Exception('Invalid relation: missing comparison operator')

        if not isinstance(val, (list, str, int, float)):
            raise Exception('Invalid relation')

        compare = compare.lower()

        if compare in operators:
            return f'{keyword} {operators[compare]} {val}'
        elif compare == 'ex':
            if val:
                # val == True
                return f'{keyword} IS NOT NULL'
            else:
                return f'{keyword} IS NULL'
        elif compare == 'between':
            if not isinstance(val, list) or len(val) != 2:
                raise Exception('Invalid relation')
            return f'{keyword} BETWEEN {val[0]} AND {val[1]}'
        elif compare == 'in':
            if not isinstance(val, list):
                raise Exception('Invalid relation')
            return f'{keyword} IN ({",".join(val)})'
        else:
            raise Exception(f'Unsupported comparison operator: {compare}')

    def build_condition(self, conditions):
        if not isinstance(conditions, dict):
            raise TypeError('conditions must be a dict')
        query = []
        for key, value in conditions.items():

            if not isinstance(value, dict):
                if value is None:
                    query.append(f'{self.decorate_key(key)} is null')
                else:
                    query.append(f'{self.decorate_key(key)} = "{value}"')
            elif key not in ['and', 'or'] and isinstance(value, dict):
                query.append(self.generate_rela(self.decorate_key(key), value))
            elif key in ['and', 'or'] and isinstance(value, dict):
                inner_query = []
                deep = 0
                for inner_key, inner_value in value.items():
                    deep += 1

                    if not isinstance(inner_value, dict):
                        if inner_value is None:
                            query.append(f'{self.decorate_key(inner_key)} is null')
                        else:
                            inner_query.append(f'{self.decorate_key(inner_key)} = "{inner_value}"')

                    elif isinstance(inner_value, dict):
                        inner_query.append(self.generate_rela(self.decorate_key(inner_key), inner_value))

                    else:
                        raise Exception('Invalid condition')
                else:
                    if deep <= 1:
                        raise Exception('Invalid relation')
                if key == 'and':
                    query.append(f"({' AND '.join(inner_query)})")
                elif key == 'or':
                    query.append(f"({' OR '.join(inner_query)})")
        if len(query) > 1:
            return f"{' AND '.join(query)}"
        else:
            return f"{' '.join(query)}"

    def build_init(self):
        self.base = self.param.get('base', None)
        if not self.base:
            raise Exception('Base must be specified')

        table = self.base.get('table', None)
        if not table:
            raise Exception('Table must be specified')

        way = self.base.get('way', None)
        if not way:
            raise Exception('Way must be specified')
        self.build_ways(way)

    def build_ways(self, way):
        if way == 'select':
            self.build_select()
        elif way == 'insert':
            self.build_insert()
        elif way == 'update':
            self.build_update()
        elif way == 'delete':
            self.build_delete()
        else:
            raise Exception(f'Unsupported usage: {way}')

    def build_select(self):
        self.query.append('SELECT')
        self.build_keys()
        self.query.append('FROM')
        table_info = [f"`{self.base.get('table', None)}`"]
        alias = self.base.get('alias', None)
        if alias:
            table_info.append(f'AS {alias}')
        self.query.append(' '.join(table_info))
        self.build_join()
        self.build_where()
        self.build_group()
        self.build_having()
        self.build_order()
        self.build_limit()
        self.build_offset()

    def build_insert(self):
        self.query.append('INSERT INTO')
        values = self.param.get('values', None)
        if not values:
            raise Exception('Values must be specified')
        if not isinstance(values, dict):
            raise Exception('Values must be dict')
        keys = [f'{self.decorate_key(k)}' for k in values.keys()]
        # vals = [f'"{v}"' for v in values.values()]
        self.query.append(f'{self.decorate_key(self.base.get("table", None))}({", ".join(keys)})')
        self.query.append('VALUES')
        decorate_vals = ['null' if v is None else f'"{v}"' for v in values.values()]
        self.query.append(f'({", ".join(decorate_vals)})')

    def build_update(self):
        self.query.append('UPDATE')
        self.query.append(self.decorate_key(self.base.get("table", None)))
        self.query.append('SET')
        values = self.param.get('values', None)
        if not values:
            raise Exception('Values must be specified')
        if not isinstance(values, dict):
            raise Exception('Values must be dict')
        sets = [f'{self.decorate_key(key)} = "{val}"' for key, val in values.items()]
        self.query.append(', '.join(sets))
        self.build_where()

    def build_delete(self):
        self.query.append(f'DELETE FROM')
        self.query.append(self.decorate_key(self.base.get("table", None)))
        self.build_where()

    def build_keys(self):
        keys = self.param.get('keys', None)
        if not keys:
            self.query.append('*')
        elif isinstance(keys, list):
            keys = [f'{self.decorate_key(k)}' for k in keys]
            self.query.append(','.join(keys))
        else:
            raise Exception(f'Unsupported keys: {keys}')

    def build_join(self):
        joins = self.param.get('joins', None)
        if not joins:
            return
        joins_query = []
        for values in joins:
            types = values.get('style', None)
            if not types:
                joins_query.append(f'INNER JOIN')
            elif types.lower() == 'left':
                joins_query.append(f'LEFT JOIN')
            elif types.lower() == 'right':
                joins_query.append(f'RIGHT JOIN')
            elif types.lower() == 'inner':
                joins_query.append(f'INNER JOIN')
            else:
                raise Exception(f'Unsupported type: {types}')

            table = values.get('table', None)
            if not table:
                raise Exception(f'Missing table')
            else:
                joins_query.append(f'`{table}`')

            alias = values.get('alias', None)
            if alias:
                joins_query.append(f'AS `{alias}`')

            on_condition = values.get('on', None)
            if not on_condition:
                raise Exception(f'Missing conditions for on')
            else:
                joins_query.append(f'ON')
                joins_query.append(self.build_condition(on_condition))
        self.query.append(' '.join(joins_query))

    def build_where(self):
        where = self.param.get('where', None)
        if not where:
            return
        self.query.append('WHERE')
        self.query.append(self.build_condition(self.param['where']))

    def build_group(self):
        groups = self.param.get('group', None)
        if not groups:
            return
        if not isinstance(groups, list):
            raise Exception(f'Invalid group: {groups}')

        self.query.append('GROUP BY')

        self.query.append(','.join([f'{self.decorate_key(key)}' for key in groups]))

    def build_having(self):
        havings = self.param.get('having', None)
        if not havings:
            return
        if not isinstance(havings, dict):
            raise Exception(f'Invalid having: {havings}')
        self.query.append('HAVING')
        self.query.append(self.build_condition(havings))

    def build_order(self):
        orders = self.param.get('order', None)
        if not orders:
            return
        if not isinstance(orders, list):
            raise Exception(f'Invalid order: {orders}')
        self.query.append('ORDER BY')

        order_query = []
        for order in orders:
            if isinstance(order, (tuple, list)):
                order_query.append(f'{self.decorate_key(order[0])} {order[1].upper()}')
            elif isinstance(order, str):
                order_query.append(f'{self.decorate_key(order)}')
        self.query.append(', '.join(order_query))

    def build_limit(self):
        limits = self.param.get('limit', None)
        if not limits:
            return
        self.query.append(f'LIMIT {int(limits)}')

    def build_offset(self):
        offsets = self.param.get('offset', None)
        if not offsets:
            return
        self.query.append(f'OFFSET {int(offsets)}')

    def build(self):
        self.build_init()
        self.sql = f' '.join(self.query) + ';'
        return self


if __name__ == '__main__':
    # params = {
    #     # 必要
    #     'base': {
    #         'table': 'user',
    #         'alias': 'us',
    #         'way': 'select'
    #     },
    #     # select 可用
    #     'joins': [
    #         {
    #             'table': 'users',  # 表名
    #             'alias': 'u',  # 别名
    #             'style': 'LEFT',  # 连接方式
    #             'on': {  # 连接条件
    #                 'and': {
    #                     'u.id': 'us.id',
    #                     'u.score': 'us.score',
    #                 },
    #             }
    #         },
    #         {
    #             'table': 'orders',  # 表名
    #             'alias': 'o',  # 别名
    #             'style': 'INNER',  # 连接方式
    #             'on': {  # 连接条件
    #                 'o.id': 'us.id'
    #             }
    #         }
    #     ],
    #     # update/delete/selct 可用
    #     'where': {  # where条件
    #         'and': {
    #             'id': {'neq': 1},  # id不等于1
    #             'age': {'lt': 30},
    #             'score': {'gte': 80},
    #         },
    #         'or': {
    #             'id': {'neq': 1},
    #             'age': {'lt': 30},
    #         },
    #         'id': 2
    #     },
    #     # select 可用
    #     'group': ['age', 'score'],
    #     # select 可用
    #     'having': {
    #         'COUNT(id)': {'gte': 5},
    #         'AVG(score)': {'lt': 90}
    #     },
    #     # select 可用
    #     'order': [('name', 'desc'), 'age'],
    #     # select 可用
    #     'limit': 10,
    #     # select 可用
    #     'offset': 0,
    #     # select 可用
    #     'keys': ['id', 'name'],
    #     # insert/update 必要
    #     'values': {
    #         'age': 30,
    #         'score': 80,
    #     }
    # }
    # res = QueryBuild(params).build().sql
    # print(res)
    #
    # params['base']['way'] = 'delete'
    # res = QueryBuild(params).build().sql
    # print(res)
    # params['base']['way'] = 'insert'
    # res = QueryBuild(params).build().sql
    # print(res)
    # params['base']['way'] = 'update'
    # res = QueryBuild(params).build().sql
    # print(res)
    pass

    q = Query()
    q.base.table = 'a'
    d = Query()
    d.base.table = 'b'
    print(d.build())
