from statistics import quantiles

from fastapi import APIRouter,Depends,status
from database import get_db
from order.schema import CardItemSchema
from sqlalchemy.orm import Session
from  fastapi.exceptions import HTTPException
from fastapi_jwt_auth2 import AuthJWT
from users.models import User
from order.models import Order,OrderItem,Product,Cart,Category,CartItem

router=APIRouter(prefix='/order')

@router.post('/add_to_cart')
def add_to_cart(data: CardItemSchema, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        user = db.query(User).filter(User.user_name == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="User topilmadi")

        cart = db.query(Cart).filter(Cart.user_id == user.id).first()
        if not cart:
            cart = Cart(user=user)
            db.add(cart)
            db.commit()
            db.refresh(cart)

        item = CartItem(cart=cart, product_id=data.product_id, quantity=data.quantity)
        db.add(item)
        db.commit()
        db.refresh(item)

        return {
            'status': status.HTTP_201_CREATED,
            'message': 'Mahsulot qoshildi'
        }

    except Exception as e:
        raise HTTPException(detail="Siz hali ro'yxatdan o'tmagansiz ", status_code=status.HTTP_400_BAD_REQUEST)
