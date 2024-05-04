import subprocess, pytest, requests, json, boto3, random, jwt, time

lambda_client = boto3.client('lambda')
ssm_client = boto3.client('ssm')

def create_jwt_token(secret_key, payload):
    token = jwt.encode(
        payload={**payload},
        key=secret_key,
        algorithm='HS256'
    )
    return token

def put_ssm_parameter(name):
    secret_key = '%030x' % random.randrange(16**30)
    response = ssm_client.put_parameter(
        Name = name,
        Value = secret_key,
        Type = 'SecureString',
        Overwrite = True
    )
    return secret_key

def create_function_url_config(function_name):
    secret_key = put_ssm_parameter('kms-key')
    print(f'secret: {secret_key}')
    token = create_jwt_token(secret_key, {"token": secret_key})
    print(f'token: {token}')
    response = lambda_client.create_function_url_config(
        FunctionName = function_name,
        AuthType = 'NONE'
    )['FunctionUrl']
    print(f'URL: {response}')
    return response, token

@pytest.fixture(scope = "module", autouse = True)
def get_end_point(request):
    subprocess.run(['podman', 'compose', 'down', '--volumes'])
    subprocess.run(['podman', 'compose', 'up', '--detach'])
    subprocess.run(['serverless', 'person:deploy', '--stage', 'local'])
    time.sleep(30)

    end_point, token = create_function_url_config('person-local-api')

    def cleanup():
        subprocess.run(['podman', 'compose', 'down', '--volumes'])

    request.addfinalizer(cleanup)
    
    return end_point, token

def post_person(service_url, header, person_id, data):
    return requests.post(service_url + '/' + person_id, headers = header, json = data)

def get_person(service_url, header, person_id):
    return requests.get(service_url + '/' + person_id, headers = header)

def put_person(service_url, header, person_id, data):
    return requests.put(service_url + '/' + person_id, headers = header, json = data)

def test_post_person(get_end_point):
    end_point, token = get_end_point
    header = { 'Authorization': f'Bearer {token}' }
    response = post_person(end_point, header, "gomesjm", {"name": "Gomes, J.M.", "title": "Bobo"})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0
    assert "POST" in response_data
    assert "data" in response_data["POST"]

def test_get_person(get_end_point):
    end_point, token = get_end_point
    header = { 'Authorization': f'Bearer {token}' }
    person_id = "cursinoc"
    response = post_person(end_point, header, person_id, {"name": "Cursino, Carla", "title": "PhD Candidate"})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0
    assert "POST" in response_data
    assert "data" in response_data["POST"]
    response_data = response_data["POST"]["data"]
    response = get_person(end_point, header, person_id)
    response_data = response.json()
    assert len(response_data) > 0
    assert "GET" in response_data
    assert "data" in response_data["GET"]
    response_data = json.loads(response_data["GET"]["data"])
    assert "name" in response_data
    assert response_data["name"] == "Cursino, Carla"

def test_put_person(get_end_point):
    end_point, token = get_end_point
    header = { 'Authorization': f'Bearer {token}' }
    person_id = "cursinoc2"
    response = post_person(end_point, header, person_id, {"name": "Cursino, Carla", "title": "PhD Candidate"})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0
    assert "POST" in response_data
    assert "data" in response_data["POST"]
    response = put_person(end_point, header, person_id, {"name": "Cursino, Carla", "title": "PhD"})
    response_data = response.json()
    assert len(response_data) > 0
    assert "PUT" in response_data
    assert "item" in response_data["PUT"]
    assert "data" in response_data["PUT"]["item"]
    response_data = json.loads(response_data["PUT"]["item"]["data"]["S"])
    assert "name" in response_data
    assert response_data["title"] == "PhD"
    response = get_person(end_point, header, person_id)
    response_data = response.json()
    assert len(response_data) > 0
    assert "GET" in response_data
    assert "data" in response_data["GET"]
    response_data = json.loads(response_data["GET"]["data"])
    assert "name" in response_data
    assert response_data["title"] == "PhD"
