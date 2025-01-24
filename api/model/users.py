from sqlalchemy import Column, INTEGER, BIGINT, VARCHAR
from src.library.model import ModelBase


class Users(ModelBase):
    __tablename__ = 'users'

    id = Column(INTEGER, primary_key=True, nullable=False)
    username = Column(VARCHAR)
    nickname = Column(VARCHAR)
    password = Column(VARCHAR)
    email = Column(VARCHAR)
    phone = Column(VARCHAR)
    ltime = Column(BIGINT)
    lip = Column(VARCHAR)
    lstatus = Column(INTEGER)
    cname = Column(INTEGER)
    uname = Column(INTEGER)
    ctime = Column(BIGINT)
    utime = Column(BIGINT)
    status = Column(INTEGER)

