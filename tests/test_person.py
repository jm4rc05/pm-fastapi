import requests
from pytest import fixture
from decouple import config
from dotenv import load_dotenv


load_dotenv('.env.local')

HOST_URL = 'http://localhost:8000'
SERVICE_URL = f'{HOST_URL}/person'


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
