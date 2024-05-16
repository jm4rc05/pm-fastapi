from fastapi import FastAPI, Request, Response
from mangum import Mangum
from ariadne.asgi import GraphQL
from api.db.database import session_factory, Base, engine
from api.middleware.authorization import AuthorizationMiddleware
from api.resolvers import person, resource
from api.security.jwt import is_authorized


api = FastAPI()

@api.on_event('startup')
def startup():
    Base.metadata.create_all(bind = engine)

api.add_middleware(AuthorizationMiddleware)

api.mount('/person/', GraphQL(person.schema(), debug = True))
api.mount('/resource/', GraphQL(resource.schema(), debug = True))

handler = Mangum(api)
