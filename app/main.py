import logging
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi_logger.logger import log_request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import datetime, timedelta, timezone
from ariadne.asgi import GraphQL
from decouple import config
from api.db.database import session_factory, Base, engine
from api.db.models.account import Account, Token
from api.middleware.authorization import user, token, authenticate
from api.resolvers import person, resource


logger = logging.getLogger()
logger.setLevel(config('LOG_LEVEL', default = 'INFO'))

api = FastAPI()

@api.on_event('startup')
async def startup():
    Base.metadata.create_all(bind = engine)

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
        access = token(data = { 'sub': account.name }, delta = timedelta(minutes = 30))

    return Token(token = access, type = 'bearer')

persons_app = GraphQL(person.schema(), debug = True)

@api.post('/person/')
@log_request
async def person(request: Request, user: Annotated[Account, Depends(user)]):
    return await persons_app.http_handler.graphql_http_server(request)

resources_app = GraphQL(resource.schema(), debug = True)

@api.post('/resource/')
@log_request
async def resource(request: Request, user: Annotated[Account, Depends(user)]):
    return await resources_app.http_handler.graphql_http_server(request)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:api', host='0.0.0.0', port=8000, reload = True)
