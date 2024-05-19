import jwt, hashlib, logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from decouple import config
from starlette.middleware.base import BaseHTTPMiddleware


SECRET_KEY = config('SECRET_KEY')

logger = logging.getLogger()
logger.setLevel(config('LOG_LEVEL', default = 'INFO'))

def is_authorized(request):
    authorization = request.headers.get('Authorization')
    if not authorization:
        logger.error('Missing or invalid password')
        return False

    try:
        bearer = authorization.split(' ')[1]
        decoded = jwt.decode(bearer, SECRET_KEY, algorithms=['HS256'])
        username = decoded.get('username')
        password = decoded.get('password')
        logger.info(f'U: {username}, P: {password}')
        
        if password != SECRET_KEY:
            logger.error('Wrong password')
            return False
    except jwt.ExpiredSignatureError:
        logger.error('Token has expired')
        return False
    except jwt.InvalidTokenError:
        logger.error('Invalid password')
        return False
    
    logger.info(f'Access authorized')

    return True

class AuthorizationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, next):
        if not is_authorized(request):
            log = 'Not authorized'
            logger.error(log)
            return JSONResponse(content = { 'ERROR': { 'message': log } }, status_code = 401)

        return await next(request)
