#!/bin/zsh

export endpoint_app='http://localhost:8000/'

export ADMIN_KEY=`openssl rand -hex 32`
export ADMIN_SALT=`openssl rand -hex 16`
export SECRET_KEY=`openssl rand -hex 16`
echo "ADMIN_KEY="$ADMIN_KEY > .env.local
echo "ADMIN_SALT="$ADMIN_SALT >> .env.local
echo "SECRET_KEY="$SECRET_KEY >> .env.local


function setup() {
    pipenv lock && pipenv requirements > requirements.txt

    # Cleanup - recria os containers
    docker compose down --volumes
    docker rmi app/api:latest
    docker compose up --detach
}

function login() {
    export authorization_token=`curl -X POST ${endpoint_app}token/ -s -H 'Content-Type: application/x-www-form-urlencoded' --data-urlencode 'username=admin' --data-urlencode 'password='$ADMIN_KEY | jq -r '.token'`
}

function person() {
    # Unauthorized
    curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -d '{"query": "{ persons { name title } }"}'

    # Authorized
    curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Carla\", title: \"PhD\") { name, title } }" }'
    
    curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Pedro\", title: \"Undergraduate\") { name, title } }" }'
    
    curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Zé\", title: \"Bocó\") { name, title } }" }'
    
    curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "{ persons { name title } }"}'
    
    curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { update(id: 1, name: \"Carla\", title: \"PhD Candidate\") { id, name, title } }" }'
    
    curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { delete(id: 2) }" }'
    
    curl -X POST ${endpoint_app}person/ -H'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "{ persons { name title } }"}'
}

function resource() {
    # Unauthorized
    curl -X POST ${endpoint_app}resource/ -H 'Content-Type: application/json' -d '{"query": "{ resources { name description } }"}'
    
    # Authorized
    curl -X POST ${endpoint_app}resource/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Sala90\", description: \"Sala de 90 lugares\") { name, description } }" }'
    
    curl -X POST ${endpoint_app}resource/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Lab90\", description: \"Laboratório de 90 bancadas\") { name, description } }" }'
    
    curl -X POST ${endpoint_app}resource/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Aud90\", description: \"Auditório de 90 lugares\") { name, description } }" }'
    
    curl -X POST ${endpoint_app}resource/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "{ resources { name description } }"}'
    }

function main() {
    setup

    login

    printf '\nexport authorization_token='$authorization_token
    printf '\nexport endpoint_app='${endpoint_app}'\n'

    person
    resource
}

main
