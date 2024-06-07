import os, logging, logging.config, jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Union
from fastapi import Request, Response, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import subqueryload
from decouple import config
from dotenv import load_dotenv
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from starlette.middleware.base import BaseHTTPMiddleware
from api.db.database import session_factory
from api.db.models.account import Account, Token
from api.middleware.secret import Secret


load_dotenv('.env.local')

logging.config.fileConfig('logging.conf')

secret = Secret()

context = CryptContext(schemes = ['sha256_crypt'])
oauth2 = OAuth2PasswordBearer(tokenUrl = 'token')


def authenticate(username: str, password: str) -> Account:
    error = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED, 
        detail = 'Could not validate credentials', 
        headers = { 'WWW-Authenticate': 'Bearer' }
    )

    with session_factory() as db:
        account = db.scalars(select(Account).filter(Account.name == username).options(subqueryload(Account.roles))).first()
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

def user(data: Annotated[str, Depends(oauth2)]) -> dict:
    error = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED, 
        detail = 'Could not validate credentials', 
        headers = { 'WWW-Authenticate': 'Bearer' }
    )

    try:
        payload = jwt.decode(data, secret.key, algorithms = ['HS256'])
        username: str = payload.get('username')
        if username is None:
            logging.info('Username not informed')
            raise error
        roles: [str] = payload.get('roles')

        return { 'username': username, 'roles':  roles }
    except jwt.InvalidTokenError:
        logging.info('Invalid token provided')
        raise error

def token(data: dict, delta: Union[timedelta, None] = None) -> str:
    payload = data.copy()

    if delta:
        expiration = datetime.now(timezone.utc) + delta
    else:
        expiration = datetime.now(timezone.utc) + timedelta(seconds = app.main.API_TOKEN_DURATION)
    payload.update({ 'exp': expiration })

    return jwt.encode(payload, secret.key, algorithm = 'HS256')


class RoleCheck:

    def __init__(self, allowed):
        self.allowed = allowed

    def __call__(self, user: Annotated[dict, Depends(user)]):
        error = HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = 'Not enough permissions'
        )

        if any(allowed == role for role in user['roles'] for allowed in self.allowed):
            return True

        raise error
