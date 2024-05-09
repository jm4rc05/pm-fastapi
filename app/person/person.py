import os

from util.common import is_authorized, logger

import boto3

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from mangum import Mangum

from ariadne.asgi import GraphQL

from graph.queries import person

api = FastAPI()

@api.middleware('http')
async def dispatch(request: Request, next):
    if not is_authorized(request):
        log = 'Not authorized'
        logger.error(log)
        return JSONResponse(content = { 'ERROR': { 'message': log } }, status_code = 401)

    return await next(request)

api.mount('/person/', GraphQL(person.schema, debug = True))

handler = Mangum(api, lifespan = 'off')
