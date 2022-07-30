from rsa import verify
from sqlalchemy import (Boolean, Column, String, ForeignKey, Float, )
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import desc
from .base import BaseModel
from datetime import datetime
from connections import postgres_db
import hashlib

def gen_pass_hash(password):
    raw = password + 'fsgteam'
    raw = raw.encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()

def check_password_hash(user_pass, password):
    return gen_pass_hash(password) == user_pass

class User(BaseModel):
    __tablename__ = "users"
    name = Column(String)
    email = Column(String)
    username = Column(String)
    password = Column(String)
    phone = Column(String)
    address = Column(String)
    role = Column(String)
    verify = Column(Boolean, default=False)
    orders = relationship("Order", backref="user")

    def __init__(self, email, password):
        self.email = email
        self.password = gen_pass_hash(password)

    @classmethod
    def authenticate(cls, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        
        if not email or not password:
            return None
        db = postgres_db()
        user = db.query(User).filter(User.email == email).first()
        if not user or not check_password_hash(user.password, password):
            return None
        return user
