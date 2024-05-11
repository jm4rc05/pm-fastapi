import jwt

from decouple import config

import boto3

import logging

logger = logging.getLogger()
logger.setLevel(config('LOG_LEVEL', default = 'INFO'))

def secret():
    ssm = boto3.client('ssm')
    try:
        response = ssm.get_parameter(Name = 'kms-api-key', WithDecryption = True)
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(e.response)
        return None

def is_authorized(request):
    authorization = request.headers.get('Authorization')
    if not authorization:
        logger.error('Missing or invalid authentication token')
        return False

    try:
        token = authorization.split(' ')[1]
        password = secret()
        decoded_token = jwt.decode(token, password, algorithms=['HS256'])
        token = decoded_token.get('token')
        SECRET_KEY = config('SECRET_KEY')
        if token != SECRET_KEY:
            logger.warning('Invalid token')
            return False
    except jwt.ExpiredSignatureError:
        logger.error('Token has expired')
        return False
    except jwt.InvalidTokenError:
        logger.error('Invalid token')
        return False
    
    logger.info('User authorized')
    return True

def encrypt(data):
    kms = boto3.client('kms')
    key_id = secret()
    response = kms.encrypt(
        KeyId=key_id,
        Plaintext=data.encode()
    )
    encrypted_data = response['CiphertextBlob']

    return encrypted_data
