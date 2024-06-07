import os, logging, logging.config, json
import redis.asyncio as redis
from fastapi import FastAPI, Request, Response, Depends, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_route_logger_middleware import RouteLoggerMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated
from datetime import datetime, timedelta, timezone
from math import ceil
from decouple import config
from dotenv import load_dotenv
from Secweb import SecWeb
from api.db.database import session_factory, Base, engine
from api.db.models.account import Account, Token
from api.middleware.authorization import user, token, authenticate, RoleCheck
from api.resolvers import sales, profiles


load_dotenv('.env.local')

logging.config.fileConfig('logging.conf')

API_PORT = config('API_PORT', cast = int, default = 8000)
API_RELOAD = config('API_RELOAD', cast = bool, default = True)
API_LIMITER_RATE = config('API_LIMITER_RATE', cast = int, default = 2)
API_LIMITER_TIME = config('API_LIMITER_TIME', cast = int, default = 5)
API_TOKEN_DURATION = config('API_TOKEN_DURATION', cast = int, default = 60)

logging.info(f'Limiter rate: {API_LIMITER_RATE} by {API_LIMITER_TIME} seconds')
logging.info(f'Token duration: {API_TOKEN_DURATION}')

REDIS_PASSWORD = config('REDIS_PASSWORD')
REDIS_HOST = config('REDIS_HOST', default = 'localhost')
REDIS_PORT= config('REDIS_PORT', cast = int, default = 6379)
REDIS_DATABASE = config('REDIS_DATABASE', cast = int, default = 0)
REDIS_PREFIX = config('REDIS_PREFIX', default = 'pm')

async def expiration(request: Request, response: Response, pexpire: int):
    expire = ceil(pexpire / 1000)

    raise HTTPException(
        status_code = status.HTTP_429_TOO_MANY_REQUESTS,
        detail = 'Too Many Requests', 
        headers = { 'Retry-After': str(expire) }
    )

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind = engine)

    redis_connection = redis.Redis(
        host = REDIS_HOST, 
        port = REDIS_PORT,
        password = REDIS_PASSWORD, 
        db = REDIS_DATABASE
    )
    await FastAPILimiter.init(
        redis_connection, 
        prefix = REDIS_PREFIX, 
        http_callback = expiration
    )

    yield

    await FastAPILimiter.close()

api = FastAPI(lifespan = lifespan)

api.add_middleware(RouteLoggerMiddleware)

@api.post('/token', dependencies = [Depends(RateLimiter(times = API_LIMITER_RATE, seconds = API_LIMITER_TIME))])
async def login(response: Response, data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    account = authenticate(data.username, data.password)
    if account is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Incorrect username or password',
            headers = {'WWW-Authenticate': 'Bearer'},
        )
    else:
        access = token(
            data = { 
                'username': account.name, 
                'roles': [role.name for role in account.roles] 
            }, 
            delta = timedelta(seconds = API_TOKEN_DURATION)
        )

    return Token(token = access, type = 'bearer')

@api.post(
    '/profiles',
    dependencies = [Depends(RateLimiter(
        times = API_LIMITER_RATE,
        seconds = API_LIMITER_TIME
    ))]
)
async def get_profiles(
    _: Annotated[bool, Depends(RoleCheck(allowed = ['admin']))],
    request: Request, 
    user: Annotated[Account, Depends(user)]
):
    return await profiles.serve(request)

@api.post(
    '/sales',
    dependencies = [Depends(RateLimiter(
        times = API_LIMITER_RATE,
        seconds = API_LIMITER_TIME
    ))]
)
async def get_sales(
    _: Annotated[bool, Depends(RoleCheck(allowed = ['user', 'admin']))],
    request: Request, 
    user: Annotated[Account, Depends(user)]
):
    return await sales.serve(request)

with open('headers.json') as settings:
     SecWeb(
        app = api, 
        Option = json.load(settings), 
        Routes = [route.path for route in api.routes]
    )

if __name__ == '__main__':
    from uvicorn import run
    run(
        'main:api', 
        server_header = False, 
        host = '0.0.0.0', 
        port = API_PORT, 
        reload = API_RELOAD
    )
