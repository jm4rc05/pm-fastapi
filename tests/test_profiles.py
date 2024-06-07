import jwt
import pytest, requests, pprint
from pytest import fixture
from time import sleep
from datetime import datetime, timedelta, timezone
from decouple import config
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv('.workspace.env')
print(f'*** ADMIN_KEY *** {config("ADMIN_KEY")} ***')

HOST_URL = 'http://localhost:8000'
SERVICE_URL = f'{HOST_URL}/profiles'


@fixture(scope = 'module', autouse = True)
def get_token(request):
    response = requests.post(
        f'{HOST_URL}/token', 
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }, 
        data = { 'username': 'admin', 'password': config('ADMIN_KEY') }
    )
    if response.status_code == 200:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {response.json()["token"]}',
        }
    else:
        return False

@fixture(scope = 'module', autouse = True)
def get_forged_token(request):
    data = { 
        'username': 'admin', 
        'roles': ['admin', 'user'],
        'exp': datetime.now(timezone.utc) + timedelta(seconds = 10000)
    }
    
    token = jwt.encode(data, 'I DO NOT HAVE A CLUE', algorithm = 'HS256')
    
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

def test_get_forged_token(get_forged_token):
    header = get_forged_token
    response = requests.post(
        SERVICE_URL,
        headers = header,
        json = { 'query': '{ account(id: 2) { name roles { id name } } }' }
    )
    print(response.json())
    assert response.status_code == 401

def test_get_account(get_token):
    header = get_token
    response = requests.post(
        SERVICE_URL,
        headers = header,
        json = { 'query': '{ account(id: 2) { name roles { id name } } }' }
    )
    print(response.json())
    assert response.status_code == 200
