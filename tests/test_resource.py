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
    token = create_jwt_token(secret_key, {"token": secret_key})
    response = lambda_client.create_function_url_config(
        FunctionName = function_name,
        AuthType = 'NONE'
    )
    return response['FunctionUrl'], token

def run(cmd):
    subprocess.run(cmd, capture_output = True, shell = True)

@pytest.fixture(scope="module", autouse=True)
def get_end_point(request):
    run('podman compose down --volumes')
    run('podman compose up --detach')
    run('serverless resource:deploy --stage local')
    time.sleep(20)

    end_point, token = create_function_url_config('resource-local-api')

    def cleanup():
        subprocess.run(['podman', 'compose', 'down', '--volumes'])

    request.addfinalizer(cleanup)
    
    return end_point, token

def post_resource(service_url, header, resource_id, data):
    return requests.post(service_url + '/' + resource_id, headers = header, json = data)

def get_resource(service_url, header, resource_id):
    return requests.get(service_url + '/' + resource_id, headers = header)

def put_resource(service_url, header, resource_id, data):
    return requests.put(service_url + '/' + resource_id, headers = header, json = data)

def test_post_resource(get_end_point):
    end_point, token = get_end_point
    header = { 'Authorization': f'Bearer {token}' }
    response = post_resource(end_point, header, 'sala90', {"description": "Sala 90", "chairs": 90})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0
    assert "POST" in response_data
    assert "data" in response_data["POST"]

def test_get_resource(get_end_point):
    end_point, token = get_end_point
    header = { 'Authorization': f'Bearer {token}' }
    resource_id = "sala120"
    response = post_resource(end_point, header, resource_id, {"description": "Sala 120", "chairs": 120})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0
    assert "POST" in response_data
    assert "data" in response_data["POST"]
    data = response_data["POST"]["data"]
    response = get_resource(end_point, header, resource_id)
    response_data = response.json()
    assert len(response_data) > 0
    assert "GET" in response_data
    assert "data" in response_data["GET"]
    data = json.loads(response_data["GET"]["data"])
    assert "description" in data
    assert data["description"] == "Sala 120"

def test_put_resource(get_end_point):
    end_point, token = get_end_point
    header = { 'Authorization': f'Bearer {token}' }
    resource_id = "sala120"
    response = post_resource(end_point, header, resource_id, {"description": "Sala 60", "chairs": 60})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0
    assert "POST" in response_data
    assert "data" in response_data["POST"]
    data = response_data["POST"]["data"]
    response = put_resource(end_point, header, resource_id, {"description": "Sala 60+20", "chairs": 80})
    response_data = response.json()
    assert len(response_data) > 0
    assert "PUT" in response_data
    assert "item" in response_data["PUT"]
    assert "data" in response_data["PUT"]["item"]
    data = json.loads(response_data["PUT"]["item"]["data"]["S"])
    assert "description" in data
    assert data["chairs"] == 80
    response = get_resource(end_point, header, resource_id)
    response_data = response.json()
    assert len(response_data) > 0
    assert "GET" in response_data
    assert "data" in response_data["GET"]
    data = json.loads(response_data["GET"]["data"])
    assert "description" in data
    assert data["chairs"] == 80
