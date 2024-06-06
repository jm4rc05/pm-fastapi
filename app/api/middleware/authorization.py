import os, logging, jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Union
from fastapi import Request, Response, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from decouple import config
from dotenv import load_dotenv
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from starlette.middleware.base import BaseHTTPMiddleware
from api.db.database import session_factory
from api.db.models.account import Account, Token
from api.middleware.secret import Secret


load_dotenv('.env.local')

secret = Secret()

API_TOKEN_DURATION = config('API_TOKEN_DURATION', cast = int, default = 60)
logging.info(f'Token duration: {API_TOKEN_DURATION}')

context = CryptContext(schemes = ['sha256_crypt'])
oauth2 = OAuth2PasswordBearer(tokenUrl = 'token')


def authenticate(username: str, password: str) -> Account:
    error = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED, 
        detail = 'Could not validate credentials', 
        headers = { 'WWW-Authenticate': 'Bearer' }
    )

    with session_factory() as db:
        account = db.query(Account).filter(Account.name == username).first()
        try:
            if account and context.verify(password, account.key):
                logging.info(f'Authenticated user {username}')
                return account
            else:
                logging.info(f'Invalid credentials for user {username}')
                raise error
        except UnknownHashError:
            logging.info(f'Error validating credentials for user {username}')
            raise error

def token(data: dict, delta: Union[timedelta, None] = None) -> str:
    payload = data.copy()

    if delta:
        expiration = datetime.now(timezone.utc) + delta
    else:
        expiration = datetime.now(timezone.utc) + timedelta(seconds = API_TOKEN_DURATION)
    payload.update({ 'exp': expiration })

    return jwt.encode(payload, secret.key, algorithm = 'HS256')

def user(data: Annotated[str, Depends(oauth2)]) -> dict:
    error = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED, 
        detail = 'Could not validate credentials', 
        headers = { 'WWW-Authenticate': 'Bearer' }
    )

    try:
        payload = jwt.decode(data, secret.key, algorithms = ['HS256'])
        username: str = payload.get('sub')
        if username is None:
            logging.info('Username not informed')
            raise error

        return { 'username': username }
    except jwt.InvalidTokenError:
        logging.info('Invalid token provided')
        raise error
