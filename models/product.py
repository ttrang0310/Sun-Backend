from sqlalchemy import (Column, String, Float, ARRAY, PickleType, Integer, ForeignKey)
from sqlalchemy.orm import backref, relationship
from .base import BaseModel


class Product(BaseModel):
    __tablename__ = "products"
    price = Column(Float, default=None)
    imgs = Column(ARRAY(PickleType))
    description = Column(String)
    title = Column(String)
    quantity = Column(Integer, default=0)
    items = relationship("Item", backref="product")
    category = Column(String)