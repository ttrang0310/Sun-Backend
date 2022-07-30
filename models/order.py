from sqlalchemy import (Boolean, Column, String, ForeignKey, Float, )
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import desc
from .base import BaseModel
from datetime import datetime


class Order(BaseModel):
    __tablename__ = "orders"
    status = Column(Boolean, default=False)
    total = Column(Float, default=None)
    user_id = Column(String, ForeignKey('users.id'))
