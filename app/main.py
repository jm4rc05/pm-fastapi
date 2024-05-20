import logging
from fastapi import FastAPI, Request, Response
from mangum import Mangum
from ariadne.asgi import GraphQL
from decouple import config
from api.db.database import session_factory, Base, engine
from api.middleware.authorization import AuthorizationMiddleware, login
from api.resolvers import person, resource


logger = logging.getLogger()
logger.setLevel(config('LOG_LEVEL', default = 'INFO'))

api = FastAPI()

@api.on_event('startup')
async def startup():
    Base.metadata.create_all(bind = engine)

api.add_middleware(AuthorizationMiddleware)

persons_app = GraphQL(person.schema(), debug = True)

@api.get('/token/')
async def token(request: Request):
    return login(request)

@api.post('/person/')
async def person(request: Request):
    return await persons_app.http_handler.graphql_http_server(request)

resources_app = GraphQL(resource.schema(), debug = True)

@api.post('/resource/')
async def resource(request: Request):
    return await resources_app.http_handler.graphql_http_server(request)

handler = Mangum(api)
