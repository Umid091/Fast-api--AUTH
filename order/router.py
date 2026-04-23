from fastapi import APIRouter, Depends, status
from database import get_db
from order.schema import CardItemSchema, UpdateCartItemSchema, OrderStatusSchema
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth2 import AuthJWT
from users.models import User
from order.models import Order, OrderItem, Product, Cart, CartItem

router = APIRouter(prefix='/order')



def get_current_user(Authorize: AuthJWT, db: Session):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token yaroqsiz")
    user = db.query(User).filter(User.user_name == current_user).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foydalanuvchi topilmadi")
    return user



@router.post('/add_to_cart', status_code=status.HTTP_201_CREATED)
def add_to_cart(data: CardItemSchema, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = get_current_user(Authorize, db)

    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    if not product.is_available or product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="Mahsulot mavjud emas yoki zaxira yetarli emas")

    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        cart = Cart(user=user)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == data.product_id
    ).first()

    if existing_item:
        existing_item.quantity += data.quantity
        db.commit()
    else:
        item = CartItem(cart=cart, product_id=data.product_id, quantity=data.quantity)
        db.add(item)
        db.commit()

    return {'status': 201, 'message': "Mahsulot savatga qo'shildi"}


@router.get('/cart')
def view_cart(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = get_current_user(Authorize, db)

    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart or not cart.items:
        return {'items': [], 'total': 0}

    items = []
    total = 0
    for item in cart.items:
        subtotal = float(item.product.price) * item.quantity
        total += subtotal
        items.append({
            'id': item.id,
            'product_id': item.product_id,
            'product_name': item.product.name,
            'price': float(item.product.price),
            'quantity': item.quantity,
            'subtotal': subtotal,
        })

    return {'items': items, 'total': round(total, 2)}


@router.patch('/cart/{item_id}')
def update_cart_item(item_id: int, data: UpdateCartItemSchema, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = get_current_user(Authorize, db)

    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Savat topilmadi")

    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Savat elementi topilmadi")

    if data.quantity <= 0:
        db.delete(item)
    else:
        item.quantity = data.quantity
    db.commit()

    return {'status': 200, 'message': 'Savat yangilandi'}


@router.delete('/cart/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(item_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = get_current_user(Authorize, db)

    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Savat topilmadi")

    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Savat elementi topilmadi")

    db.delete(item)
    db.commit()


@router.delete('/cart', status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = get_current_user(Authorize, db)

    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Savat topilmadi")

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()



@router.post('/checkout', status_code=status.HTTP_201_CREATED)
def create_order(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = get_current_user(Authorize, db)

    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Savat bo'sh")

    total_price = 0
    order = Order(user=user, total_price=0)
    db.add(order)
    db.flush()

    for item in cart.items:
        product = item.product
        if not product.is_available or product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"'{product.name}' mahsuloti yetarli emas")

        price = float(product.price) * item.quantity
        total_price += price

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )
        db.add(order_item)
        product.stock -= item.quantity

    order.total_price = round(total_price, 2)

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    db.refresh(order)

    return {'status': 201, 'message': 'Buyurtma yaratildi', 'order_id': order.id}


@router.get('/orders')
def list_orders(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = get_current_user(Authorize, db)

    orders = db.query(Order).filter(Order.user_id == user.id).all()
    result = []
    for order in orders:
        result.append({
            'id': order.id,
            'status': order.status,
            'total_price': float(order.total_price),
            'created_at': order.created_at,
            'items_count': len(order.items),
        })

    return result


@router.get('/orders/{order_id}')
def get_order(order_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = get_current_user(Authorize, db)

    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

    items = []
    for item in order.items:
        items.append({
            'product_id': item.product_id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': float(item.price),
            'subtotal': float(item.price) * item.quantity,
        })

    return {
        'id': order.id,
        'status': order.status,
        'total_price': float(order.total_price),
        'created_at': order.created_at,
        'items': items,
    }


@router.patch('/orders/{order_id}/cancel')
def cancel_order(order_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = get_current_user(Authorize, db)

    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    if order.status != Order.OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Faqat 'pending' holatidagi buyurtmani bekor qilish mumkin")

    order.status = Order.OrderStatus.cancelled

    for item in order.items:
        item.product.stock += item.quantity

    db.commit()

    return {'status': 200, 'message': 'Buyurtma bekor qilindi'}




