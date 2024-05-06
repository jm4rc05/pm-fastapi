import os

from util.common import is_authorized, logger

import boto3

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

from mangum import Mangum

from starlette.middleware.base import BaseHTTPMiddleware

from ariadne.asgi import GraphQL

from ariadne import load_schema_from_path, QueryType, MutationType, make_executable_schema

from util.database import SessionLocal, engine

def get_db():
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    database = os.environ["POSTGRES_DATABASE"]

    SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    logger.info(f'Connection URL: {SQLALCHEMY_DATABASE_URL}')
    # db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()

api = FastAPI()

defs = load_schema_from_path('schema')
query = QueryType()
mutation = MutationType()

persons_db = []

@query.field("persons")
def persons(*_):
    logger.info('Query persons')
    return persons_db

@mutation.field("add")
def add(_, info, name, title, db: Session = Depends(get_db)):
    persons_db.append({ "name": name, "title": title })
    return {"name": name, "title": title }

schema = make_executable_schema(defs, [query, mutation])

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, next):
        if not is_authorized(request):
            log = 'Not authorized'
            logger.error(log)
            return JSONResponse(content = { 'ERROR': { 'message': log } }, status_code = 401)

        return await next(request)

api.add_middleware(AuthMiddleware)

api.mount("/person/", GraphQL(schema, debug = True))

handler = Mangum(api, lifespan = "off")
