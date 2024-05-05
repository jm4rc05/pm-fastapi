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
    logger.info('Getting database')
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

api = FastAPI()

defs = load_schema_from_path('schema')
query = QueryType()
mutation = MutationType()

resources_db = []

@query.field("resources")
def resources(*_):
    logger.info('Query resources')
    return resources_db

@mutation.field("add")
def add(_, info, name, description, db: Session = Depends(get_db)):
    resources_db.append({ "name": name, "description": description })
    return {"name": name, "description": description }

schema = make_executable_schema(defs, [query, mutation])

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, next):
        if not is_authorized(request):
            log = 'Not authorized'
            logger.error(log)
            return JSONResponse(content = { 'ERROR': { 'message': log } }, status_code = 401)

        return await next(request)

api.add_middleware(AuthMiddleware)

api.mount("/resource/", GraphQL(schema, debug = True))

handler = Mangum(api, lifespan = "off")
