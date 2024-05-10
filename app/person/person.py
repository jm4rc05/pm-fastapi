import os

from util.common import is_authorized, logger

import boto3

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from mangum import Mangum

from ariadne.asgi import GraphQL
from graph.queries import person

api = FastAPI()

if __name__ != "__person__":
    @api.middleware('http')
    async def dispatch(request: Request, next):
        if not is_authorized(request):
            log = 'Not authorized'
            logger.error(log)
            return JSONResponse(content = { 'ERROR': { 'message': log } }, status_code = 401)

        return await next(request)

api.mount('/person/', GraphQL(person.schema('graph'), debug = True))

if __name__ == "__person__":
    import uvicorn 

    uvicorn.run("person:api", host="0.0.0.0", reload=True, port=8000)
else: 
    handler = Mangum(api, lifespan = 'off')
