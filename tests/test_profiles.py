import jwt
import pytest, requests, pprint
from pytest import fixture
from time import sleep
from datetime import datetime, timedelta, timezone
from decouple import config
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv('.workspace.env')

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
    query = '''
        query ($id: Int) { 
            account(id: $id) { 
                name roles { 
                    id name 
                    
                } 
            } 
        }
    '''
    variables = {
        'id': 2
    }
    response = requests.post(
        SERVICE_URL,
        headers = header,
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 401

def test_get_account(get_token):
    header = get_token
    query = '''
        query ($id: Int) { 
            account(id: $id) { 
                name roles { 
                    id name 
                    
                } 
            } 
        }
    '''
    variables = {
        'id': 2
    }
    response = requests.post(
        SERVICE_URL,
        headers = header,
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 200

def test_cors(get_token):
    header = get_token
    header.update({ 'Origin': 'http://example.com' })
    header.update({ 'Access-Control-Request-Method': 'POST' })
    header.update({ 'Access-Control-Request-Headers': 'X-Requested-With' })
    response = requests.options(
        SERVICE_URL,
        headers = header
    )
    pprint.PrettyPrinter(indent = 2).pprint(dict(response.headers))
    assert response.status_code == 400
    assert response.text == 'Disallowed CORS origin'
