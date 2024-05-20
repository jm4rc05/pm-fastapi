import jwt, hashlib, logging
from fastapi import Request, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from decouple import config
from passlib.context import CryptContext
from starlette.middleware.base import BaseHTTPMiddleware
from api.db.database import session_factory
from api.db.models.account import Account


SECRET_KEY = config('SECRET_KEY')

logger = logging.getLogger()
logger.setLevel(config('LOG_LEVEL', default = 'INFO'))

context = CryptContext(schemes = ['sha256_crypt'], deprecated = 'auto')
oauth2 = OAuth2PasswordBearer(tokenUrl = 'token')

async def authenticate(username: str, password: str):
    db = session_factory()
    with db as db:
        account = db.query(Account).filter(Account.name == username).first()
        if not account or not context.verify(password, account.key):
            return False

        return account

def token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm = 'HS256')

def user(token: str = Depends(oauth2)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('usename')
        if username is None:
            raise HTTPException(status_code=401, detail='Invalid authentication credentials')
        user = { 'username': username }
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail='Invalid authentication credentials')
    
    return user

def login(request):
    authorization = request.headers.get('Authorization')
    logger.info(f'Authorization: {authorization}')
    if not authorization:
        logger.error('Missing or invalid password')
        return False

    bearer = authorization.split(' ')[1]
    decoded = jwt.decode(bearer, SECRET_KEY, algorithms=['HS256'])
    username = decoded.get('username')
    password = decoded.get('password')
    logger.info(f'Login - U: {username}, P: {password}')
    account = authenticate(username, password)
    if not account:
        logger.error(f'Incorrect username {username} or password')
        return False
    
    response = { 'token': token({ 'username': username, 'password': password }), 'type': 'bearer' }

    logger.info(f'Response: {response}')

    return response





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
        logger.info(f'Authorizing - U: {username}, P: {password}')
        
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
