import os, logging.config
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import redis.asyncio as redis
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi_route_logger_middleware import RouteLoggerMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from typing import Annotated
from datetime import datetime, timedelta, timezone
from ariadne.asgi import GraphQL
from sqladmin import Admin
from decouple import config
from dotenv import load_dotenv
from api.db.database import session_factory, Base, engine
from api.db.models.account import Account, AccountAdmin, Token
from api.middleware.authorization import user, token, authenticate
from api.resolvers import person, resource


load_dotenv('.env.local')

API_PORT = config('API_PORT', cast = int, default = 8000)
API_RELOAD = config('API_RELOAD', cast = bool, default = True)
API_LIMITER_RATE = config('API_LIMITER_RATE', cast = int, default = 2)
API_LIMITER_TIME = config('API_LIMITER_TIME', cast = int, default = 5)
API_TOKEN_DURATION = config('API_TOKEN_DURATION', cast = int, default = 30)

REDIS_PASSWORD = config('REDIS_PASSWORD')
REDIS_HOST = config('REDIS_HOST', default = 'localhost')
REDIS_PORT= config('REDIS_PORT', cast = int, default = 6379)
REDIS_DATABASE = config('REDIS_DATABASE', cast = int, default = 0)
REDIS_PREFIX = config('REDIS_PREFIX', default = 'pm')

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind = engine)

    redis_connection = redis.Redis(
        host = REDIS_HOST, 
        port = REDIS_PORT,
        password = REDIS_PASSWORD, 
        db = REDIS_DATABASE
    )
    await FastAPILimiter.init(redis_connection, prefix = REDIS_PREFIX)

    yield

    await FastAPILimiter.close()

api = FastAPI(lifespan = lifespan)
admin = Admin(api, engine)
admin.add_view(AccountAdmin)

logging.config.fileConfig(f'{os.path.dirname(os.path.realpath(__file__))}/logging.conf')
api.add_middleware(RouteLoggerMiddleware)

@api.post('/token', dependencies=[Depends(RateLimiter(times = API_LIMITER_RATE, seconds = API_LIMITER_TIME))])
async def login(data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    account = authenticate(data.username, data.password)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    else:
        access = token(data = { 'sub': account.name }, delta = timedelta(minutes = API_TOKEN_DURATION))

    return Token(token = access, type = 'bearer')

persons_app = GraphQL(person.schema(), debug = True)

@api.post('/person', dependencies = [Depends(RateLimiter(times = API_LIMITER_RATE, seconds = API_LIMITER_TIME))])
async def person(request: Request, user: Annotated[Account, Depends(user)]):
    return await persons_app.http_handler.graphql_http_server(request)

resources_app = GraphQL(resource.schema(), debug = True)

@api.post('/resource', dependencies = [Depends(RateLimiter(times = API_LIMITER_RATE, seconds = API_LIMITER_TIME))])
async def resource(request: Request, user: Annotated[Account, Depends(user)]):
    return await resources_app.http_handler.graphql_http_server(request)

if __name__ == '__main__':
    from uvicorn import run
    run('main:api', host = '0.0.0.0', port = API_PORT, reload = API_RELOAD)
