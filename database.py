from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import create_engine 

engine = create_engine("postgresql://postgres:123@localhost:5432/fast_auth",echo=True)

Base = declarative_base()


SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()