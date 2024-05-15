from fastapi import Request, Response
from fastapi.responses import JSONResponse

from starlette.middleware.base import BaseHTTPMiddleware

from api.util.common import is_authorized, logger


class AuthorizationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, next):
        if not is_authorized(request):
            log = 'Not authorized'
            logger.error(log)
            return JSONResponse(content = { 'ERROR': { 'message': log } }, status_code = 401)

        return await next(request)
