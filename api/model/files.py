from sqlalchemy import Column, BIGINT, INTEGER, VARCHAR
from src.library.model import ModelBase


class Files(ModelBase):
    __tablename__ = 'files'

    id = Column(INTEGER, primary_key=True, nullable=False)
    oname = Column(VARCHAR)
    mdname = Column(VARCHAR)
    mime = Column(VARCHAR)
    cname = Column(INTEGER)
    uname = Column(INTEGER)
    ctime = Column(BIGINT)
    utime = Column(BIGINT)
    status = Column(INTEGER)

