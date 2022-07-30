from sqlalchemy import (String, Integer, Column, Float, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import desc
from .base import BaseModel
from datetime import datetime


class Item(BaseModel):
    __tablename__ = "items"
    quantity = Column(Integer, default=1)
    product_id = Column(String, ForeignKey('products.id'))
    amount = Column(Float, default=None)
    order = relationship("Order", backref="items")
    order_id = Column(String, ForeignKey("orders.id"))