import os, logging.config
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi_route_logger_middleware import RouteLoggerMiddleware
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

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind = engine)

    yield

api = FastAPI(lifespan = lifespan)
admin = Admin(api, engine)
admin.add_view(AccountAdmin)

logging.config.fileConfig(f'{os.path.dirname(os.path.realpath(__file__))}/logging.conf')
api.add_middleware(RouteLoggerMiddleware)

@api.post('/token')
async def login(data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    account = authenticate(data.username, data.password)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    else:
        access = token(data = { 'sub': account.name }, delta = timedelta(minutes = config('API_TOKEN_DURATION', cast = int)))

    return Token(token = access, type = 'bearer')

persons_app = GraphQL(person.schema(), debug = True)

@api.post('/person')
async def person(request: Request, user: Annotated[Account, Depends(user)]):
    return await persons_app.http_handler.graphql_http_server(request)

resources_app = GraphQL(resource.schema(), debug = True)

@api.post('/resource')
async def resource(request: Request, user: Annotated[Account, Depends(user)]):
    return await resources_app.http_handler.graphql_http_server(request)

if __name__ == '__main__':
    from uvicorn import run
    run('main:api', host = '0.0.0.0', port = config('API_PORT', cast = int), reload = config('API_RELOAD', cast = bool))
