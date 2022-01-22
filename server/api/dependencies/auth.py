from fastapi import Depends
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm.session import Session
from starlette.requests import Request
from pydantic.networks import EmailStr

from jose import JWTError, ExpiredSignatureError

from api import schemas
from api.core import security
from api.core.exceptions import CredentialsException
from api.crud.user import UserCrud
from api.dependencies.db import get_db
from datetime import datetime


def get_token(request: Request):
    header_authorization = request.headers.get("Authorization")
    _, header_param = get_authorization_scheme_param(header_authorization)
    return header_param


def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    """Decode the provided jwt and extract the user using the [sub] field."""
    if not token:
        return None
    try:
        payload = security.decode_token(token)
        email = payload.sub
        if email is None:
            # Something wrong with the token
            raise CredentialsException
        # Get user from database
        user = UserCrud.get_user_by_email(db, email)
        if user is None:
            raise CredentialsException
        return user
    except (JWTError, ExpiredSignatureError):
        # Something wrong with the token
        raise CredentialsException

# TEST ONLY - use with test_main.py to skip authentication
# def get_current_user() -> schemas.User:
#    user = schemas.User(id=1, email="test@test.com", created_at=datetime.now(), updated_at=datetime.now())
#    return user
