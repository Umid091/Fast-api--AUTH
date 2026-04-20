from fastapi import FastAPI
from users.router import router as user_router
from users.schemas import Settings
from fastapi_jwt_auth2 import AuthJWT
from users.models import BlacklistedToken
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from database import get_db

from fastapi import  Depends, status


app = FastAPI()
app.include_router(router=user_router)


@AuthJWT.load_config
def get_config():
    return Settings()




def check_blacklist(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    jti = Authorize.get_raw_jwt()["jti"]

    token = db.query(BlacklistedToken).filter(BlacklistedToken.jti == jti).first()
    if token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token bekor qilingan, qayta login qiling"
        )