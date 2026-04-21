from database import Base

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    user_name = Column(String(50), unique=True,index=True)
    first_name = Column(String(50),nullable=True)
    email = Column(String,unique=True,index=True)
    password = Column(String(300))

    is_staff = Column(Boolean,default=False)
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime,default=datetime.now())
    updated_at = Column(DateTime,default=datetime.now())

    orders = relationship('Order', back_populates='user')
    cart = relationship('Cart', back_populates='user')


    def __repr__(self):
        return f"<User {self.user_name}>"
    

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True)
    jti = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)