import pytest, requests, pprint
from pytest import fixture
from time import sleep
from decouple import config
from dotenv import load_dotenv


load_dotenv('.env.local')
load_dotenv('.env.test.local')

HOST_URL = 'http://localhost:8000'
SERVICE_URL = f'{HOST_URL}/person'


@fixture(scope = 'module', autouse = True)
def get_token(request):
    response = requests.post(
        f'{HOST_URL}/token', 
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }, 
        data = { 'username': 'admin', 'password': config('ADMIN_KEY') }
    )
    if response.status_code == 200:
        return response.json()['token']
    else:
        return False

@fixture(scope = 'module', autouse = True)
def get_token_wrong_password(request):
    response = requests.post(
        f'{HOST_URL}/token', 
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }, 
        data = { 'username': 'admin', 'password': 'wrong_password' }
    )
    if response.status_code == 200:
        return response.json()['token']
    else:
        return False

@fixture(scope = 'module', autouse = True)
def get_token_wrong_user(request):
    response = requests.post(
        f'{HOST_URL}/token', 
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }, 
        data = { 'username': 'wrong_user', 'password': 'wrong_password' }
    )
    if response.status_code == 200:
        return response.json()['token']
    else:
        return False

def test_unauthorized():
    header = {
        'Content-Type': 'application/json',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        data = '{"query": "{ persons { name title } }"}'
    )
    assert response.status_code == 401

def test_invalid_token():
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcxNjU3MDU2OX0.LDhZ5aTKuvttlBaN2ZTIcxntyHTEZHdCaa8_9u8Er3U'
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        data = '{"query": "{ persons { name title } }"}'
    )
    assert response.status_code == 401

def test_wrong_password(get_token_wrong_password):
    token = get_token_wrong_password
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        data = '{"query": "{ persons { name title } }"}'
    )
    assert response.status_code == 401

def test_wrong_user(get_token_wrong_user):
    token = get_token_wrong_user
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        data = '{"query": "{ persons { name title } }"}'
    )
    assert response.status_code == 401

def test_add_person(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { add(name: "Carla", title: "PhD") { name, title } }' }
    )
    print(response.json())
    assert response.status_code == 200
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { add(name: "Zé", title: "Bocó") { name, title } }' }
    )
    print(response.json())
    assert response.status_code == 200
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { add(name: "Pedro", title: "Undergraduate") { name, title } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_update_person(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { update(id: 1, name: "Carla", title: "PhD Candidate") { id, name, title } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_delete_person(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { delete(id: 2) }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_list_persons(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': '{ persons { name title } }' }
    )
    print(response.json())
    assert response.status_code == 200

@pytest.mark.skip
def test_cost(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': '{ persons { name title } }' }
    )
    print(response.json())
    assert response.status_code == 200
    
@pytest.mark.skip
@pytest.mark.order(before = 'test_token_duration')
def test_rate_limit(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    for _ in range(1, config('API_LIMITER_RATE', cast = int) + 10):
        response = requests.post(
            SERVICE_URL, 
            headers = header, 
            json = { 'query': '{ persons { name title } }' }
        )
        assert response.status_code == 200 or 429
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': '{ persons { name title } }' }
    )
    pprint.PrettyPrinter(indent = 2).pprint(dict(response.headers))
    assert response.status_code == 429

@pytest.mark.order('last')
def test_token_duration(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    snooze = config('API_TOKEN_DURATION', cast = int) + 1
    sleep(snooze)
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': '{ persons { name title } }' }
    )
    print(response.json())
    assert response.status_code == 401
