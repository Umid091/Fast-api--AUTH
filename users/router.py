from http.client import responses

from sqlalchemy import Update
from sqlalchemy.sql.functions import current_time

from users.models import User,BlacklistedToken
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from fastapi.exceptions import HTTPException
from users.schemas import SignUpSchema as SignUp, LoginSchema as Login,UpdateUser,PasswordUpdate
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth2 import AuthJWT

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
        "user_name": data.user_name,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

@router.get('/profile')
def profile_view(Authorize : AuthJWT=Depends(),db: Session = Depends(get_db)):
    try:
        Authorize.jwt_required()
        current_user =Authorize.get_jwt_subject()
        print(current_user,'--==================================')

    except Exception as e:
        raise  HTTPException(detail=f'error:{e}',status_code=status.HTTP_400_BAD_REQUEST)


    db_user =db.query(User).filter(User.user_name==current_user).first()
    return {
        "user_name": db_user.user_name,
        "first_name": db_user.first_name,
        "email": db_user.email
    }





@router.put('/update')
def update(data:UpdateUser, Authorize :AuthJWT=Depends(),db: Session =Depends(get_db)):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        print("Token dagi user+++++++++++++:", current_user)

        all_users = db.query(User).all()
        print("DB dagi userlar:++++++++++++++++=======", [u.user_name for u in all_users])

        db_user =db.query(User).filter(User.user_name==current_user).first()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foydalanuvchi topilmadi"
            )

        for i,j in data.model_dump().items():
            setattr(db_user,i,j)
        db.commit()
        db.refresh(db_user)

    except Exception as e:
        raise HTTPException(detail=f'error:{e}', status_code=status.HTTP_400_BAD_REQUEST)

    return {
        "massage":"Malumotlaringgzi muvofaqiyatli o'zgartirildi",

        "user_name": db_user.user_name,
        "first_name": db_user.first_name,
        "email": db_user.email
        }




@router.put('/update_pass')
def update_pass(data:PasswordUpdate, Authorize :AuthJWT=Depends(),db: Session =Depends(get_db)):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        db_user =db.query(User).filter(User.user_name==current_user).first()

        check_user = check_password_hash(db_user.password,data.old_password)
        if not check_user:
            raise HTTPException(detail='Oldingi parolingiz xato',status_code=status.HTTP_400_BAD_REQUEST)

        if data.old_password ==data.new_password:
            raise HTTPException(detail="Yangi parol eski parolga teng bolmasin",status_code=status.HTTP_400_BAD_REQUEST)

        if data.confirm_password != data.new_password:
            raise HTTPException(detail="Yangi parolllar bir biriga teng emas",status_code=status.HTTP_400_BAD_REQUEST)

        db_user.password= generate_password_hash(data.new_password)

        db.commit()
        db.refresh(db_user)

    except Exception as e:
        raise HTTPException(detail=f'error:{e}', status_code=status.HTTP_400_BAD_REQUEST)

    return {
        "massage":"Parolingiz muvofaqiyatli yangilandi",

        "user_name": db_user.user_name,
        "first_name": db_user.first_name,
        "email": db_user.email
        }



@router.get('/login_refresh')
def login_refresh(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_refresh_token_required()
        current_user =Authorize.get_jwt_subject()

        access_token =Authorize.create_access_token(subject=str(current_user))

        return {
            'status':status.HTTP_201_CREATED,
            'access_token':access_token
        }
    except Exception as e:
        raise HTTPException(detail=f"{e}",status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/logout')
def logout(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()

        jti = Authorize.get_raw_jwt()["jti"]

        blacklisted = BlacklistedToken(jti=jti)
        db.add(blacklisted)
        db.commit()

        return {
            "status": status.HTTP_200_OK,
            "message": f"{current_user} tizimdan chiqdi"
        }
    except Exception as e:
        raise HTTPException(detail=f"{e}", status_code=status.HTTP_400_BAD_REQUEST)




