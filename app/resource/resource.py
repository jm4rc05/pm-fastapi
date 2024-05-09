import os

from util.common import is_authorized, logger

import boto3

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse

from mangum import Mangum

from ariadne.asgi import GraphQL

api = FastAPI()

resources_db = []

@api.middleware('http')
async def dispatch(request: Request, next):
    if not is_authorized(request):
        log = 'Not authorized'
        logger.error(log)
        return JSONResponse(content = { 'ERROR': { 'message': log } }, status_code = 401)

    return await next(request)

api.mount('/resource/', GraphQL(schema, debug = True))

handler = Mangum(api, lifespan = 'off')
