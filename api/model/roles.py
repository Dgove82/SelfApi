from sqlalchemy import Column, VARCHAR, BIGINT, INTEGER
from src.library.model import ModelBase


class Roles(ModelBase):
    __tablename__ = 'roles'

    id = Column(INTEGER, primary_key=True, nullable=False)
    role = Column(VARCHAR)
    rrank = Column(INTEGER)
    cname = Column(INTEGER)
    uname = Column(INTEGER)
    ctime = Column(BIGINT)
    utime = Column(BIGINT)
    status = Column(INTEGER)

