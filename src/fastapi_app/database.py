from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , DeclarativeBase

db_url = "sqlite:///./blog.db"

engine = create_engine(db_url , connect_args={"check_same_thread" : False})
sessionLocal = sessionmaker(bind = engine , autoflush = False , autocommit = False)


class Base(DeclarativeBase):
    pass

def get_db():
    with sessionLocal() as db:
        yield db