import pytest, requests, pprint, json
from pytest import fixture
from time import sleep
from decouple import config
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv('.workspace.env')


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
    query = '''
        mutation ($name: String) { 
            addCategory(name: $name) { 
                name 
            } 
        }
    '''
    variables = {
        'name': 'Categoria descategorizada'
    }
    response = requests.post(
        SERVICE_URL,
        headers = header,
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 200

def test_add_address(get_token):
    header = get_token
    query = '''
        mutation ($street: String, $city: String, $county: String, $postal: String, $country: String) { 
            addAddress(street: $street, city: $city, county: $county, postal: $postal, country: $country) { 
                street, city, county, postal, country 
            } 
        }
    '''
    variables = {
        'street': 'rua das Casas', 
        'city': 'Cidade das Ruas', 
        'county': 'Condado das Cidades', 
        'postal': '00.000-000', 
        'country': 'País dos Manés'
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 200

def test_add_shop(get_token):
    header = get_token
    query = '''
        mutation ($name: String, $category: Int, $address: Int) { 
            addShop(name: $name, category: $category, address: $address) { 
                name 
            } 
        }
    '''
    variables = {
        'name': 'Loja de Teste',
        'category': 1, 
        'address': 1
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 200

def test_add_customer(get_token):
    header = get_token
    query = '''
        mutation ($name: String, $category: Int, $address: Int) { 
            addCustomer(name: $name, category: $category, address: $address) { 
                name 
            } 
        }
    '''
    variables = {
        'name': 'Zé', 
        'category': 1, 
        'address': 1
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 200

def test_get_category(get_token):
    header = get_token
    query = '''
        query ($id: Int!) { 
            category(id: $id) { 
                name 
            } 
        }
    '''
    variables = {
        'id': 1
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 200

def test_update_category(get_token):
    header = get_token
    query = '''
        mutation ($id: Int, $name: String) { 
            updateCategory(id: $id, name: $name) { 
                name 
            } 
        }
    '''
    variables = {
        'id': 1,
        'name': 'Categoria categorizada'
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 200

def test_update_address(get_token):
    header = get_token
    query = '''
        mutation ($id: Int, $street: String, $city: String, $county: String, $postal: String, $country: String) { 
            updateAddress(id: $id, street: $street, city: $city, county: $county, postal: $postal, country: $country) { 
                street, city, county, postal, country 
            } 
        }
    '''
    variables = {
        'id': 1, 
        'street': 'rua Esburacada', 
        'city': 'Cidade sem Ruas', 
        'county': 'Condado das Vilas Perdidas', 
        'postal': '00.000-000', 
        'country': 'País dos Buracos'
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 200

def test_update_shop(get_token):
    header = get_token
    query = '''
        mutation ($id: Int!, $name: String) { 
            updateShop(id: $id, name: $name) { 
                id
                name 
            } 
        }
    '''
    variables = {
        'id': 1,
        'name': 'Loja de Inutilidades'
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'variables': variables, 'query': query }
    )
    print(response.json())
    assert response.status_code == 200

def test_update_customer(get_token):
    header = get_token
    query = '''
        mutation ($id: Int, $name: String) { 
            updateCustomer(id: $id, name: $name) { 
                name 
            }
        }
    '''
    variables = {
        'id': 1, 
        'name': 'Mané'
    }
    print(query)
    print(variables)
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 200

def test_add_product(get_token):
    header = get_token
    query = '''
        mutation ($name: String, $price: Float) { 
            addProduct(name: $name, price: $price) { 
                name price 
            } 
        }
    '''
    variables = {
        'name': 'Produto contrabandeado', 
        'price': 1000.00
    }
    response = requests.post(
        SERVICE_URL,
        headers = header,
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 200

def test_cost(get_token):
    header = get_token
    query = '''
        query category($id: Int) { 
            category(id: $id) { 
                name 
                customers { 
                    id 
                    name 
                    orders { 
                        id 
                        shop { name } 
                        items { 
                            product { 
                                name 
                                price 
                            } 
                            quantity 
                            value 
                        } 
                    } 
                } 
                shops { 
                    id 
                    name 
                    sales { 
                        id 
                        customer { 
                            name 
                            orders { 
                                id 
                                shop { name } 
                                items { 
                                    product { 
                                        name 
                                        price 
                                    } 
                                    quantity 
                                    value 
                                } 
                            }
                        } 
                        items { 
                            product { name } 
                            quantity 
                            value 
                        } 
                    } 
                } 
            } 
        }      
    '''
    variables = { 'id': 1 }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code >= 400

@pytest.mark.order(before = 'test_token_duration')
def test_rate_limit(get_token):
    header = get_token
    query = '''
        query ($id: Int) {
            category(id: $id) { 
                name 
            }
        }
    '''
    variables = {
        'id': 1
    }
    for _ in range(1, config('API_LIMITER_RATE', cast = int) + 10):
        response = requests.post(
            SERVICE_URL, 
            headers = header, 
            json = { 'query': query, 'variables': variables }
        )
        assert response.status_code == 200 or 429
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': query, 'variables': variables }
    )
    pprint.PrettyPrinter(indent = 2).pprint(dict(response.headers))
    assert response.status_code == 429

@pytest.mark.order('last')
def test_token_duration(get_token):
    header = get_token
    snooze = config('API_TOKEN_DURATION', cast = int) + 1
    sleep(snooze)
    query = '''
        query ($id: Int) {
            category(id: $id) { 
                name 
            }
        }
    '''
    variables = {
        'id': 1
    }
    response = requests.post(
        SERVICE_URL, 
        headers = header, 
        json = { 'query': query, 'variables': variables }
    )
    print(response.json())
    assert response.status_code == 401
