# Project Management

Arquivo `.gitignore`:

```
.serverless
*.pyc
*.pyo
node_modules
```

Arquivo `person.py`:

```python
from flask import Flask
app = Flask(__name__)
 
@app.route("/")
def hello():
    return "Hello World!"
```

Arquivo `serverless.yml`:

```yml
service: people
 
provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  memorySize: 128
```

Instalar plugins:

```sh
pipenv install
pipenv shell
pipenv install Flask werkzeug boto3

sls people:plugin install -n serverless-wsgi
sls people:plugin install -n serverless-python-requirements
sls people:plugin install -n serverless-localstack

pipenv lock && pipenv requirements > people/requirements.txt
```

Revisar `serverless.yml`:

```yml
service: people
 
provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  memorySize: 128

plugins:
  - serverless-wsgi
  - serverless-python-requirements
  - serverless-localstack

custom:
  localstack:
    stages:
      - local
  wsgi:
    app: person.app
    packRequirements: false

functions:
  app:
    handler: wsgi.handler
    events:
      - http: 'ANY /'
      - http: 'ANY /{proxy+}'
```

## localstack

```sh
podman compose up --detach
```

## AWS

Arquivo `~/.aws/config`:

```ini
[default]
region = us-east-1
output = json
```

Arquivo `~/.aws/credentials`:

```ini
[default]
aws_access_key_id=test
aws_secret_access_key=test
```

Endpoint URL:

```sh
export AWS_ENDPOINT_URL=http://localhost:4566
```


## Instalação

```sh
sls deploy --stage local
```

### Criar API URL e anotar endpoint

```sh
export endpoing=`aws lambda create-function-url-config --function-name people-local-api --auth-type NONE | jq '.FunctionUrl'`
```

Excluir:

```sh
aws lambda delete-function-url-config --function-name people-local-api
```



### Teste completo

```sh
podman compose down --volumes && podman compose up --detach && sls deploy --stage local

export endpoing=`aws lambda create-function-url-config --function-name people-local-api --auth-type NONE | jq '.FunctionUrl'`

curl -H "Content-Type: application/json" -X POST ${endpoint}/users -d '{"userId": "gomesjm", "name": "Gomes, J.M.", "title": "Bobo"}'

curl -H "Content-Type: application/json" -X POST ${endpoint}/users -d '{"userId": "cursinoc", "name": "Cursino, Carla", "title": "PhD Candidate"}'

curl ${endpoint}/users/cursinoc

curl -H "Content-Type: application/json" -X PUT ${endpoint}/users -d '{"userId": "cursinoc", "name": "Cursino, Carla", "title": "PhD"}'

curl ${endpoint}/users/cursinoc

curl -H "Content-Type: application/json" -X DELETE ${endpoint}/users -d '{"userId": "gomesjm"}'

curl ${endpoint}/users/gomesjm

podman compose down --volumes
```



### Remoção

```sh
podman compose down --volumes
```

## Sub-módulos

### Adicionar

```sh
git submodule add --force https://github.com/jm4rc05/pm-graph.git app/person/graph
git submodule add --force https://github.com/jm4rc05/pm-util.git app/person/util

git submodule add --force https://github.com/jm4rc05/pm-graph.git app/resource/graph
git submodule add --force https://github.com/jm4rc05/pm-util.git app/resource/util
```

### Atualizar

```sh
git submodule update --recursive --remote
```

#### Se der error

```sh
git rm app/person/graph --force
git rm app/person/util --force

git rm app/resource/graph --force
git rm app/resource/util --force
```

Em seguida re-adicionar os módulos
