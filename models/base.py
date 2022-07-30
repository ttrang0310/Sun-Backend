from sqlalchemy import (Boolean, Column, String, DateTime, Index, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from datetime import datetime
from uuid import uuid4

class utcnow(expression.FunctionElement):
    type = DateTime()

@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

def generate_uuid():
    return str(uuid4())

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    __mapper_args__ = {
        'confirm_deleted_rows': False
    }
    @declared_attr
    def __table_args__(cls):
        return (Index("idx_{}_created_status".format(cls.__name__.lower()),
                      "_created",), )

    id = Column(String(), primary_key=True, default=generate_uuid)
    _created = Column(DateTime,
                      server_default=utcnow())
    _updated = Column(DateTime,
                      server_default=utcnow())

    def to_dict(self):
        results = dict()
        for k in self.__dict__.keys():
            if k in ["_sa_instance_state", "password", "seller_id"]:
                continue
            results[k] = getattr(self, k)
        return results