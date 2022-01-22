from typing import Generator
from api.database import SessionLocal, DbInit


def get_db() -> Generator:
    """Yield a SQLAlchemy database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# get scoped SQA session for use with multi-threading in Uploads service
def get_db_scoped() -> Generator:
    """Yield a scoped SQLAlchemy database session"""
    engine = DbInit.new_engine()
    db = DbInit.new_scoped_session(engine)
    try:
        yield db
    finally:
        db.close()
