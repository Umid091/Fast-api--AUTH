from pydantic import BaseModel,Field
from  typing import Optional

class CardItemSchema(BaseModel):
    product_id :int
    quantity: int