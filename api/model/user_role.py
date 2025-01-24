from sqlalchemy import Column, INTEGER, BIGINT
from src.library.model import ModelBase


class UserRole(ModelBase):
    __tablename__ = 'user_role'

    id = Column(INTEGER, primary_key=True, nullable=False)
    rid = Column(INTEGER)
    uid = Column(INTEGER)
    cname = Column(INTEGER)
    uname = Column(INTEGER)
    ctime = Column(BIGINT)
    utime = Column(BIGINT)
    status = Column(INTEGER)

