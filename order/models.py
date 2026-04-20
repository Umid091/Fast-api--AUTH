from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, Numeric,Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String)

    products = relationship('Product', back_populates='category')


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    description  = Column(Text)
    price = Column(Float)
    stock = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now())
    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship('Category', back_populates='products')
    order_items = relationship('OrderItem', back_populates='product')
    cart_items  = relationship('CartItem', back_populates='product')



import enum

class Order(Base):
    __tablename__ = 'orders'

    class OrderStatus(str, enum.Enum):
        pending    = "pending"
        processing = "processing"
        delivered  = "delivered"
        cancelled  = "cancelled"

    id = Column(Integer, primary_key=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    total_price = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey('users.id'))

    user  = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order')

    def __repr__(self):
        return f"<Order {self.id} - {self.status}>"

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer)
    price = Column(Numeric(10, 2))
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))

    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')

class Cart(Base):
    __tablename__ = 'carts'
    id= Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='cart')
    items = relationship('CartItem', back_populates='cart')

class CartItem(Base):
    __tablename__ = 'cart_items'
    id= Column(Integer, primary_key=True)
    quantity = Column(Integer, default=1)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    product_id = Column(Integer, ForeignKey('products.id'))

    cart= relationship('Cart', back_populates='items')
    product = relationship('Product', back_populates='cart_items')

