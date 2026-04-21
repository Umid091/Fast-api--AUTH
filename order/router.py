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

@router.post('add_to_cart')
def add_card(data:CardItemSchema,db:Session=Depends(get_db()),Authorize: AuthJWT=Depends())
    try:
        Authorize.jwt_required()
        current_user=Authorize.get_jwt_subject()
        user =db.query(User).filter(id=current_user).first()

        if user.card:
            card =db.query(Cart).filter(user_id=user.id).first()

        else:
            card=Cart(user =user)
            db.add(card)
            db.commit()
            db.refresh(card)

        item =Cart(user=user,product_id =data.product_id,stock =data.stock)
        db.add(item)
        db.commit()
        db.refresh(item)

        data ={
            'status':status.HTTP_201_CREATED,
            'message':'Maxsulot qoshiladi',

        }
        return data

    except Exception as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)



