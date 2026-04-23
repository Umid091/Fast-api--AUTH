from pydantic import BaseModel
from order.models import Order

class CardItemSchema(BaseModel):
    product_id: int
    quantity: int = 1

class UpdateCartItemSchema(BaseModel):
    quantity: int

class OrderStatusSchema(BaseModel):
    status: Order.OrderStatus