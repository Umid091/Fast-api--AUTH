from fastapi import FastAPI
from users.router import router as user_router
from users.schemas import Settings
from fastapi_jwt_auth import AuthJWT

app = FastAPI()
app.include_router(router=user_router)


@AuthJWT.load_config
def get_config():
    return Settings()