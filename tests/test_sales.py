import pytest, requests, pprint
from pytest import fixture
from time import sleep
from decouple import config
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv('.workspace.env')
print(f'*** ADMIN_KEY *** {config("ADMIN_KEY")} ***')

HOST_URL = 'http://localhost:8000'
SERVICE_URL = f'{HOST_URL}/sales'


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

def test_add_category(get_token):
    header = get_token
    response = requests.post(
        SERVICE_URL,
        headers = header,
        json = { 'query': 'mutation { addCategory(name: "Categoria descategorizada") { name } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_add_address(get_token):
    header = get_token
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { addAddress(street: "rua das Casas", city: "Cidade das Ruas", county: "Condado das Cidades", postal: "00.000-000", country: "País dos Manés") { street, city, county, postal, country } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_add_shop(get_token):
    header = get_token
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { addShop(name: "Loja de Teste", category: 1, address: 1) { name } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_add_customer(get_token):
    header = get_token
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { addCustomer(name: "Zé", category: 1, address: 1) { name } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_get_category(get_token):
    header = get_token
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': '{ category(id: 1) { name } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_update_category(get_token):
    header = get_token
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { updateCategory(id: 1, name: "Categoria categorizada") { name } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_update_address(get_token):
    header = get_token
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { updateAddress(id: 1, street: "rua Esburacada", city: "Cidade sem Ruas", county: "Condado das Vilas Perdidas", postal: "00.000-000", country: "País dos Buracos") { street, city, county, postal, country } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_update_shop(get_token):
    header = get_token
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { updateShop(id: 1, name: "Loja de Inutilidades") { name } }' }
    )
    print(response.json())
    assert response.status_code == 200

def test_update_customer(get_token):
    header = get_token
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': 'mutation { updateCustomer(id: 1, name: "Mané") { name } }' }
    )
    print(response.json())
    assert response.status_code == 200

@pytest.mark.skip
def test_cost(get_token):
    header = get_token
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
    header = get_token
    for _ in range(1, config('API_LIMITER_RATE', cast = int) + 10):
        response = requests.post(
            SERVICE_URL, 
            headers = header, 
            json = { 'query': '{ category(id: 1) { name } }' }
        )
        assert response.status_code == 200 or 429
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': '{ category(id: 1) { name } }' }
    )
    pprint.PrettyPrinter(indent = 2).pprint(dict(response.headers))
    assert response.status_code == 429

@pytest.mark.skip
@pytest.mark.order('last')
def test_token_duration(get_token):
    header = get_token
    snooze = config('API_TOKEN_DURATION', cast = int) + 1
    sleep(snooze)
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': '{ category(id: 1) { name } }' }
    )
    print(response.json())
    assert response.status_code == 401

def test_add_product(get_token):
    header = get_token
    response = requests.post(
        SERVICE_URL,
        headers = header,
        json = { 'query': 'mutation { addProduct(name: "Produto contrabandeado", price: 1000.00) { name price } }' }
    )
    print(response.json())
    assert response.status_code == 200
