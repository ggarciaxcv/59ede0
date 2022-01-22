from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import Session

from dotenv import dotenv_values

config = dotenv_values(".env")

engine = create_engine(config.get("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Class DbInit is used to initialize new SQA engines and sessions for use with multi-threading.
class DbInit():
    # new_scoped_session returns a new SQA scoped session
    @classmethod
    def new_scoped_session(self, engine) -> Session:
        session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        return session
        