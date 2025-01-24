from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from src.utils.tools import ContentTool
from src.conf import SQLConfig


def generate_single_model_file(table_name, output_path='.', module_name=None):
    """
    根据表名生成单个ORM模型文件的代码字符串。

    :param table_name: 要生成模型的表名
    :param output_path: 输出文件的路径，默认为当前目录('.')
    :param module_name: 输出的Python模块文件名，如果为None，则使用表名+.py，默认为None
    """
    if module_name is None:
        module_name = f"{table_name}.py"

    # 数据库连接信息，这里需要根据实际情况修改
    url = f'{SQLConfig.ENGINE}://{SQLConfig.USER}:{SQLConfig.PASSWORD}@{SQLConfig.HOST}:{SQLConfig.PORT}/{SQLConfig.DB}'

    # 创建引擎和基础映射
    engine = create_engine(url)
    base = automap_base()
    base.prepare(autoload_with=engine)

    # 检查表名是否存在
    if table_name not in base.classes:
        print(f"表名'{table_name}'不存在于数据库中。")
        return

    # for table in Base.classes.items():
    #     print(table[0])
    # 获取表对应的类
    table_cls = base.classes[table_name]

    cols = ''
    col_types = set()

    for col in table_cls.__table__.columns:
        col_type = repr(col.type.__class__.__name__).replace("'", '')
        if col_type == 'TINYINT':
            col_type = 'INTEGER'
        col_types.add(col_type)

        primary_key_str = ", primary_key=True" if col.primary_key else ""
        nullable_str = ", nullable=False" if not col.nullable else ""
        unique_str = ", unique=True" if col.unique else ""
        index_str = ", index=True" if col.index else ""
        default_str = f", default={repr(col.default.arg)}" if col.default else ""
        # 注意：这里简化了默认值的处理，可能需要针对特定情况进一步调整

        cols += f"    {col.name} = Column({col_type}{primary_key_str}{nullable_str}{unique_str}{index_str}{default_str})\n"

    # 构建类定义的代码字符串
    class_definition = f"from sqlalchemy import Column, {', '.join(col_types)}\n"
    class_definition += f"from sqlalchemy.ext.declarative import declarative_base\n"
    class_definition += f"Base = declarative_base()\n\n\n"
    class_definition += f"class {ContentTool(table_name).multiword_construct(delimiter='_')}(Base):\n"
    class_definition += f"    __tablename__ = '{table_name}'\n\n"
    class_definition += cols
    class_definition += "\n"  # 类定义结束留空行

    # 写入文件（如果需要）
    with open(f"{output_path}/{module_name}", 'w') as f:
        f.write(class_definition)

    print(f"模型代码已成功生成至 '{output_path}/{module_name}' 文件。")


# 使用示例
table_to_generate = input("请输入表名：")
generate_single_model_file(table_to_generate)
