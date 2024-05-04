# Desenvolvendo função **AWS** _Lambda_ localmente com **Flask**, **LocalStack** e **Serverless**

## Configuração do serviço **AWS** para acesso local

Como iremos utilizar **LocalStack** e **Serverless** para desenvolvimento e testes de nossa função **AWS** _Lambda_, iremos configurar nosso ambiente de trabalho para apontar para nossa configuração local. Outra opção é utilizar o utilitário [`awslocal`](https://github.com/localstack/awscli-local) - _presume-se que já temos [**AWS** _Command Line Interface_](https://aws.amazon.com/cli/) instalado_:

### Shell

```sh
export AWS_ENDPOINT_URL=http://localhost:4566
```

### AWS

Arquivo `~.aws/config`:

```ini
[default]
region = us-east-1
output = json
```

Arquivo `~.aws/credentials`:

```ini
[default]
aws_access_key_id=test
aws_secret_access_key=test
```

## Requisitos

Além do [**AWS** _Command Line Interface_](https://aws.amazon.com/cli/), estes utilitários facilitadores foram usados neste exemplo. Para alguns existem alternativas que também podem ser usadas:

1. [git](https://git-scm.com/) - gerenciamento de versão de código fonte
1. [pipenv](https://pipenv.pypa.io/en/latest/) - gerenciamento de dependências do projeto
1. [pyenv](https://github.com/pyenv/pyenv) - gerenciamento de versão do Python
1. [podman](https://podman.io) - gerenciamento de _containers_
1. [LocalStack](https://www.localstack.cloud/) - emulação de serviços **AWS** localmente
1. [Serverless](https://www.serverless.com/) - automação do desenvolvimento de funções **AWS** _Lambda_

> Caso alguém já use [`poetry`](https://python-poetry.org/) no lugar de `pipenv`, ou [`Docker`](https://docker.com/) no lugar de `podman` ou até mesmo [`mercurial`](https://mercurial-scm.org/) ao invés de `git` mantenha sua ferramenta predileta e adapte os exemplos.

## Python

Instalar Python (se já não tiver):

```sh
pyenv install 3.11
```

> Na ocasião de escrever este tutorial o **AWS** _Lambda_ dá suporte até a versão `3.11` do **Python**.

Criar o projeto com as dependências da aplicação que vamos desenvolver:

1. [Flask](https://github.com/pallets/flask) - _framework_ leve para aplicações _web_
1. [boto3](https://github.com/boto/boto3) - _SDK_ **AWS** para aplicações **Python**
1. [pytest](https://github.com/pytest-dev/pytest/) - utilitário de testes unitários para **Python**
1. [requests](https://github.com/psf/requests) - biblioteca _HTTP_ para **Python** (usado nos testes)
1. [werkzeug](https://github.com/pallets/werkzeug) - biblioteca de interface com _Gateway_ de serviço _web_ ([WSGI - Web Service Gateway Interface](https://wsgi.readthedocs.io/en/latest/what.html))

```sh
mkdir <pasta do projeto>
cd <pasta do projeto>
pyenv local 3.11
pipenv install jwt flask boto3 werkzeug
pipenv install --dev pytest requests
touch README.md
```

Colocar projeto sob controle de versão. O arquivo [`.gitignore`](./.gitignore) - _que poderá ser gerado automaticamente em [gitignore.io](https://www.toptal.com/developers/gitignore/api/visualstudiocode,python,flask,node,localstack,serverless)_:

```sh
git init
git add .
git commit -m "<descricao do projeto>"
git remote add origin <url do repositório remoto github/gitlab/bitbucket/etc>
git push --set-upstream origin master
```

## Projeto

Adicionar pastas para os módulos do projeto (uma para cada módulo) e gerar arquivo `requirements.txt` separadamente para cada módulo. Na primeira vez, cada módulo terá o arquivo `requirements.txt` gerado a partir da raiz do projeto, e depois cada um evoluirá para ter seus próprios requisitos particulares:

```sh
mkdir <pasta do módulo 1>
pipenv lock && pipenv requirements --dev > <pasta do módulo 1>/requirements.txt
mkdir <pasta do módulo 2>
pipenv lock && pipenv requirements --dev > <pasta do módulo 2>/requirements.txt
```

> O arquivo `requirements.txt` em cada módulo é necessário para que cada um seja gerado e instalado no serviço **AWS** _Lambda_ independentemente.

> `Serverless` é capaz de usar nosso arquivo [`Pipfile`](./Pipfile) para gerenciar as dependências do módulo, e para isto teríamos que criar um arquivo `Pipfile` para cada módulo e tratar cada um como um ambiente diferente, o que adicionaria uma camada de complexidade ao gerenciamento de configuração de nossa aplicação. Para projetos maiores isso poderá ser necessário mas não é o caso ainda de nosso exemplo.

Gerar um arquivo `__init__.py` (vazio) para cada módulo:

```sh
touch <pasta do módulo 1>/__init__.py
touch <pasta do módulo 2>/__init__.py
```

## LocalStack

Criar uma configuração [**Docker Compose**](./compose.yml) para os containers **LocalStack**

```yml
version: "3.8"

services:
  localstack:
    container_name: localstack
    image: localstack/localstack
    privileged: true
    ports:
      - '4566:4566'
      - '4510-4559:4510-4559'
    networks:
      - localstack
    volumes:
      - localstackdata:/var/lib/localstack
      - /var/run/docker.sock:/var/run/docker.sock

volumes:
  localstackdata:
    name: localstackdata

networks:
  localstack:
    external: true
```


## Serverless

Vamos criar uma configuração multi-projetos para o **Serverless. Na pasta raiz criamos um arquivo [`serverless-compose.yml`](./serverless-compose.yml) que irá apontar para nossos módulos:

```yml
services:

  modulo1:
    path: <pasta do módulo 1>

  modulo2:
    path: <pasta do módulo 2>

### Plugins

Instalar os _plugins_ requeridos para este projeto:

```sh
npm i serverless-python-requirements serverless-wsgi serverless-localstack
```

### Módulos

Para a pasta de cada módulo, iremos criar a configuração individual apontada pelo arquivo [`serverless-compose.yml`](./serverless-compose.yml) acima:

```yml
service: modulo1

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  memorySize: 128
  environment:
    DYNAMODB_TABLE: ${self:service}-${opt:stage, self:provider.stage}
  iamRoleStatements:
    - Effect: Allow
      Action:
        - dynamodb:Query
        - dynamodb:Scan
        - dynamodb:GetItem
        - dynamodb:PutItem
        - dynamodb:UpdateItem
        - dynamodb:DeleteItem
      Resource: "arn:aws:dynamodb:${opt:region, self:provider.region}:*:table/${self:provider.environment.DYNAMODB_TABLE}"

plugins:
  - serverless-wsgi
  - serverless-python-requirements
  - serverless-localstack

custom:
  localstack:
    stages:
      - local
  wsgi:
    app: modulo1.api
    packRequirements: false

functions:
  app:
    handler: wsgi_handler.handler
    events:
      - http: 'ANY /'
      - http: 'ANY /{proxy+}'

resources:
  Resources:
    PersonDynamoDbTable:
      Type: 'AWS::DynamoDB::Table'
      DeletionPolicy: Retain
      Properties:
        AttributeDefinitions:
          -
            AttributeName: modulo1Id
            AttributeType: S
        KeySchema:
          -
            AttributeName: modulo1Id
            KeyType: HASH
        ProvisionedThroughput:
          ReadCapacityUnits: 1
          WriteCapacityUnits: 1
        TableName: ${self:provider.environment.DYNAMODB_TABLE}
```

## Função _Lambda_

Finalmente iremos criar o código **Python** para a função _Lambda_ de cada módulo. Neste exemplo estamos usando **AWS** _DynamoDB_ para armazenamento de dados. Como o _DynamoDB_ é um banco de dados do tipo _chave_/_valor_, não iremos definir uma estrutura de dados como faríamos com uma aplicação de negócios usando um banco de dados relacional como **PostgreSQL** ou **MySQL** (ou **AWS** _RDS_) - _neste exemplo estamos simplesmente armazenando uma estrutura de dados no formato **JSON** dentro de um registro do DynamoDB_ (arquivo `modulo1/modulo1.py`):

```python
import os

import boto3, botocore, logging, json

from flask import Flask, jsonify, request

api = Flask(__name__)

dynamodb = boto3.client('dynamodb')
table = os.environ['DYNAMODB_TABLE']

logger = logging.getLogger()
logger.setLevel('INFO')

@api.route('/modulo1/<string:modulo1_id>', methods = ['GET'])
def get(modulo1_id):
    if not modulo1_id:
        log = jsonify({ 'ERROR': { 'message': 'Please provide modulo1Id' } })
        logger.error(log)
        return log, 400

    try:
        item = dynamodb.get_item(
            TableName = table,
            Key = { 'modulo1Id': { 'S': modulo1_id } }
        ).get('Item')

        if not item:
            log = jsonify({'ERROR': { 'message': 'Resource does not exist' } })
            logger.error(log)
            return log, 404
    except botocore.exceptions.ClientError as e:
        log = jsonify({ 'ERROR': e.response })
        logger.exception(log)
        return log, 500

    log = jsonify({ 'GET': { 'modulo1Id': item.get('modulo1Id').get('S'), 'data': item.get('data').get('S'), } })
    logger.info(log)
    return log, 200

@api.route('/modulo1/<string:modulo1_id>', methods = ['POST'])
def create(modulo1_id):
    if not modulo1_id:
        log = jsonify({ 'ERROR': { 'message': 'Please provide modulo1Id' } })
        logger.error(log)
        return log, 400

    data = request.get_json()
    if not data:
        log = jsonify({ 'ERROR': { 'message': 'Please provide some data' } })
        logger.error(log)
        return log, 404

    try:
        dynamodb.put_item(
            TableName = table,
            Item = {
                'modulo1Id': { 'S': modulo1_id },
                'data': { 'S': json.dumps(data) }
            }
        )
    except botocore.exceptions.ClientError as e:
        log = jsonify({ 'EXCEPTION': e.response })
        logger.exception(log)
        return log, 500

    log = jsonify({ 'POST': { 'modulo1Id': modulo1_id, 'data': data } })
    logger.info(log)
    return log, 200

@api.route('/modulo1/<string:modulo1_id>', methods = ['PUT'])
def update(modulo1_id):
    if not modulo1_id:
        log = jsonify({ 'ERROR': { 'message': 'Please provide modulo1Id' } })
        logger.error(log)
        return log, 400

    try:
        data = request.get_json()
        if not data:
            log = jsonify({ 'ERROR': { 'message': 'Please provide some data' } })
            logger.error(log)
            return log, 400

        response = dynamodb.update_item(
            TableName = table,
            Key = { 'modulo1Id': { 'S': modulo1_id } },
            AttributeUpdates = { 'data': { 'Value': { 'S': json.dumps(data) }, 'Action': 'PUT' }, },
            ReturnValues = 'UPDATED_NEW'
        )

        if (response['ResponseMetadata']['HTTPStatusCode'] == 200):
            log = jsonify({ 'PUT': { 'modulo1Id': modulo1_id, 'item': response['Attributes'] } })
            logger.info(log)
            return log, 200
        else:
            log = jsonify({ 'ERROR': response })
            logger.error(log)
            return log, 500

    except botocore.exceptions.ClientError as e:
        log = jsonify({ 'EXCEPTION': e.response })
        log.exception(log)
        return log, 500

@api.route('/modulo1/<string:modulo1_id>', methods = ['DELETE'])
def delete(modulo1_id):
    if not modulo1_id:
        log = jsonify({ 'ERROR': { 'message': 'Please provide modulo1Id' } })
        logger.error(log)
        return log, 400

    try:
        dynamodb.delete_item(
            TableName = table,
            Key = { 'modulo1Id': { 'S': modulo1_id } }
        )
    except botocore.exceptions.ClientError as e:
        return jsonify({ 'ERROR': e.response }), 500

    log = jsonify({ 'DELETE': { 'modulo1Id': modulo1_id } })
    logger.info(log)
    return log, 200
```

### Testes

Criamos um módulo de testes para cada módulo de função _Lambda_ só para ilustração - _estes testes não possuem valor algum para verificar o funcionamento de uma aplicação e servem apenas como exercício_. Como dissemos anteriormente, não definimos uma estrutura de dados em nosso banco de dados _DynamoDB_, portanto os testes presumem valores armazenados no formato _JSON_ no banco de dados, e assim mantemos os testes de inclusão e alteração indepotentes:

```sh
mkdir tests
```

O teste irá exercitar cada um de nossas sub-funções (arquivo `tests/test_modulo1.py`):

```python
import os, pytest, requests, json

@pytest.fixture(scope="module", autouse=True)
def get_end_point(request):

    os.system("podman compose up --detach && sls modulo1:deploy --stage local")

    end_point = os.popen("aws lambda create-function-url-config --function-name modulo1-local-api --auth-type NONE | jq -r '.FunctionUrl'").read()[:-1] + 'modulo1'

    print(f"End point: {end_point}")

    def cleanup():
        os.system("podman compose down --volumes")

    request.addfinalizer(cleanup)
    
    return end_point

def post_modulo1(service_url, modulo1_id, data):
    return requests.post(service_url + '/' + modulo1_id, json = data)

def get_modulo1(service_url, modulo1_id):
    return requests.get(service_url + '/' + modulo1_id)

def put_modulo1(service_url, modulo1_id, data):
    return requests.put(service_url + '/' + modulo1_id, json = data)

def test_post_modulo1(get_end_point):
    response = post_modulo1(get_end_point, 'sala90', {"description": "Sala 90", "chairs": 90})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0
    assert "POST" in response_data
    assert "data" in response_data["POST"]

def test_get_modulo1(get_end_point):
    modulo1_id = "sala120"
    response = post_modulo1(get_end_point, modulo1_id, {"description": "Sala 120", "chairs": 120})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0
    assert "POST" in response_data
    assert "data" in response_data["POST"]
    data = response_data["POST"]["data"]
    response = get_modulo1(get_end_point, modulo1_id)
    response_data = response.json()
    assert len(response_data) > 0
    assert "GET" in response_data
    assert "data" in response_data["GET"]
    data = json.loads(response_data["GET"]["data"])
    assert "description" in data
    assert data["description"] == "Sala 120"

def test_put_modulo1(get_end_point):
    modulo1_id = "sala120"
    response = post_modulo1(get_end_point, modulo1_id, {"description": "Sala 60", "chairs": 60})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0
    assert "POST" in response_data
    assert "data" in response_data["POST"]
    data = response_data["POST"]["data"]
    response = put_modulo1(get_end_point, modulo1_id, {"description": "Sala 60+20", "chairs": 80})
    response_data = response.json()
    assert len(response_data) > 0
    assert "PUT" in response_data
    assert "item" in response_data["PUT"]
    assert "data" in response_data["PUT"]["item"]
    data = json.loads(response_data["PUT"]["item"]["data"]["S"])
    assert "description" in data
    assert data["chairs"] == 80
    response = get_modulo1(get_end_point, modulo1_id)
    response_data = response.json()
    assert len(response_data) > 0
    assert "GET" in response_data
    assert "data" in response_data["GET"]
    data = json.loads(response_data["GET"]["data"])
    assert "description" in data
    assert data["chairs"] == 80
```

O teste executa funções `shell` para ativar o **LocalStack** e fazer a instalação das funções _Lambda_ e ao término elimina os _containers_ criados, limpando todo o ambiente (veja a função `get_end_point` acima).

O _endpoint_ da função _Lambda_ sob teste é obtido dinamicamente para ser chamado via requisição _HTTP_ - _este exemplo não apresenta nenhum tipo de credencial de acessos, o que será explorado numa próxima versão_.

Também podemos ativar e instalar nossas funções para executar alguns testes interativos utilizando por exemplo [**curl**](https://curl.se) ou [**Postman**](https://www.postman.com/):

```sh
podman compose up --detach && sls deploy --stage local
```

Esta sequencia de comandos irá instalar todos os módulos do projeto.

Para fazer a instalação de um único módulo podemos usar:

```sh
podman compose up --detach && sls modulo1:deploy --stage local
```

Como fizemos em nossos testes, podemos obter o _endpoint_ da função _Lambda_ e armazena-la localmente:

```sh
export endpoint_modulo1=`aws lambda create-function-url-config --function-name modulo1-local-api --auth-type NONE | jq -r '.FunctionUrl'`
```

Em seguida para testar com **curl**:

```sh
curl -X POST ${endpoint_modulo1}/modulo1/gomesjm -H 'Content-Type: application/json' -d '{"name": "Gomes, J.M.", "title": "Developer"}'
```

> Para testar com **Postman** use o _endpoint_ retornado por `create-function-url-config` do **AWS** _CLI_.

Finalize removendo todos os _containers_ e volumes criados para os testes:

```sh
podman compose down --volumes
```
