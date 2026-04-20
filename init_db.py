from database import Base,engine
from users.models import User
from order.models import Product,Cart,Category,Order,OrderItem,CartItem

Base.metadata.create_all(bind=engine)

