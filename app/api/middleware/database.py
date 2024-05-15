from fastapi import Request, Response

from starlette.middleware.base import BaseHTTPMiddleware

from api.util.common import logger


class DatabaseMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, db):
        super().__init__(app)
        self.db = db

    async def dispatch(self, request: Request, next):
        response = Response('Internal server error', status_code = 500)

        try:
            response = await next(request)
        finally:
            self.db.close()
        
        return response
