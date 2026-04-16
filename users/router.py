from users.models import User
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from fastapi.exceptions import HTTPException
from users.schemas import SignUpSchema as SignUp, LoginSchema as Login
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def sign_up(user: SignUp, db: Session = Depends(get_db)):
    db_username = db.query(User).filter(User.user_name == user.user_name).first()
    if db_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu username band")
    
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu email band")

    new_user = User(
        user_name=user.user_name,
        first_name=user.first_name,
        email=user.email,
        password=generate_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Muvaffaqiyatli ro'yxatdan o'tdingiz", "user": new_user.user_name}


@router.post("/login", status_code=status.HTTP_200_OK)
def login(data: Login, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()): 
    db_user = db.query(User).filter(User.user_name == data.user_name).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bunday username mavjud emas")

    if not check_password_hash(db_user.password, data.password): 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parol xato")

    access_token = Authorize.create_access_token(subject=data.user_name)
    refresh_token = Authorize.create_refresh_token(subject=data.user_name)

    return {
        "message": "Muvaffaqiyatli tizimga kirdingiz",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_name": data.user_name
    }