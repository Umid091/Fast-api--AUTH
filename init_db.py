from database import Base,engine
from users.models import User

Base.metadata.create_all(bind=engine)

