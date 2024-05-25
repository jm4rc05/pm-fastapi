import os, logging, logging.config, jwt, hashlib
from datetime import datetime, timedelta, timezone
from typing import Annotated, Union
from fastapi import Request, Response, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from decouple import config
from dotenv import load_dotenv
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from starlette.middleware.base import BaseHTTPMiddleware
from api.db.database import session_factory
from api.db.models.account import Account, Token, TokenData
from constants import ROOT_DIR


logging.config.fileConfig(f'{ROOT_DIR}/logging.conf')
logger = logging.getLogger()

load_dotenv('.env.local')

SECRET_KEY = config('SECRET_KEY')
API_TOKEN_DURATION = config('API_TOKEN_DURATION', cast = int, default = 60)
logger.info(f'Token duration: {API_TOKEN_DURATION}')

context = CryptContext(schemes = ['sha256_crypt'])
oauth2 = OAuth2PasswordBearer(tokenUrl = 'token')


def authenticate(username: str, password: str) -> Account:
    with session_factory() as db:
        account = db.query(Account).filter(Account.name == username).first()
        try:
            if account and context.verify(password, account.key):
                logger.info(f'Authenticated user {username}')
                return account
            else:
                logger.info(f'Invalid credentials for user {username}')
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED, 
                    detail = 'Invalid credentials', 
                    headers = { 'WWW-Authenticate': 'Bearer' }
                )
        except UnknownHashError:
            logger.info(f'Error validating credentials for user {username}')
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED, 
                detail = 'Could not validate credentials', 
                headers = { 'WWW-Authenticate': 'Bearer' }
            )

def token(data: dict, delta: Union[timedelta, None] = None):
    payload = data.copy()

    if delta:
        expiration = datetime.now(timezone.utc) + delta
    else:
        expiration = datetime.now(timezone.utc) + timedelta(seconds = API_TOKEN_DURATION)
    payload.update({ 'exp': expiration })

    return jwt.encode(payload, SECRET_KEY, algorithm = 'HS256')

def user(data: Annotated[str, Depends(oauth2)]):
    error = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED, 
        detail = 'Could not validate credentials', 
        headers = { 'WWW-Authenticate': 'Bearer' }
    )
    try:
        payload = jwt.decode(data, SECRET_KEY, algorithms = ['HS256'])
        username: str = payload.get('sub')
        if username is None:
            logger.info('Username not informed')
            raise error

        return { 'username': username }
    except jwt.InvalidTokenError:
        logger.info('Invalid token provided')
        raise error
