import pytest, requests
from pytest import fixture
from time import sleep
from decouple import config
from dotenv import load_dotenv


load_dotenv('.env.local')

HOST_URL = 'http://localhost:8000'
SERVICE_URL = f'{HOST_URL}/resource'


@fixture(scope="module", autouse=True)
def get_token(request):
    response = requests.post(f'{HOST_URL}/token', headers = { 'Content-Type': 'application/x-www-form-urlencoded' }, data = { 'username': 'admin', 'password': config('ADMIN_KEY')})
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
        data = '{"query": "{ resources { name description } }"}'
    )
    assert response.status_code == 401

def test_add_resource(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { add(name: "Sala90", description: "Sala de 90 lugares") { name, description } }' }
    )
    print(response.json())
    assert response.status_code == 200
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { add(name: "Lab90", description: "Laboratório de 90 bancadas") { name, description } }' }
    )
    print(response.json())
    assert response.status_code == 200
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { add(name: "Aud90", description: "Auditório de 90 lugares") { name, description } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_update_resource(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { update(id: 1, name: "Sala90", description: "Sala de 90 lugares sentados") { name, description } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_delete_resource(get_token):
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

def test_list_resources(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': '{ resources { name, description } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_rate_limit(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    for _ in range(1, config('API_LIMITER_RATE', cast = int)):
        response = requests.post(
            SERVICE_URL, 
            headers = header, 
            json = { 'query': '{ resources { name description } }' }
        )
        print(response.json())
        assert response.status_code == 200 or 429
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': '{ resources { name description } }' }
    )
    print(response.json())
    assert response.status_code == 429

@pytest.mark.order('last')
def test_token_duration(get_token):
    token = get_token
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    sleep((config('API_TOKEN_DURATION', cast = int) + 1) * 60)
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': '{ resources { name description } }' }
    )
    print(response.json())
    assert response.status_code == 401
