#!/bin/zsh

function jwt() {
    header='{"alg":"HS256","typ":"JWT"}' && encoded_header=$(echo -n "$header" | base64 | tr -d '=' | tr '/+' '_-') && encoded_payload=$(echo -n "$1" | base64 | tr -d '=' | tr '/+' '_-') && header_payload="${encoded_header}.${encoded_payload}" && signature=$(echo -n "$header_payload" | openssl dgst -sha256 -hmac "${SECRET_KEY}" -binary | base64 | tr -d '=' | tr '/+' '_-')

    export authorization_token="${header_payload}.${signature}"
}

function setup() {
    # Security
    # User "admin" que será usado em `compose.yml`
    # e na função `admin()` - opcional
    echo "ADMIN_KEY=`openssl rand -hex 32`" > .env.local
    echo "ADMIN_SALT=`openssl rand -hex 16`" >> .env.local

    # Cleanup - recria os containers
    docker compose down --volumes
    docker compose up --detach
    echo 'Esperando a morte da bezerra...'
    sleep 10

    # Security
    # API
    export SECRET_KEY=`openssl rand -hex 16`

    jwt '{"username": "admin", "password": "'${SECRET_KEY}'"}'
}

function deploy() {
    # Setup dependencies
    pipenv requirements > app/requirements.txt

    # Deploy/test app
    sls app:deploy --stage local && export endpoint_app=`aws lambda create-function-url-config --function-name app-local-api --auth-type NONE | jq -r '.FunctionUrl'`
}

function admin() {
    # Create admin user
    docker exec postgres bash -c $"psql -U pmdb -d pmdb \
        INSERT INTO public.account ( \
            name, \
            key, \
            salt \
        ) VALUES ( \
            'admin', \
            '$ADMIN_KEY', \
            '$ADMIN_SALT' \
        );"

}

function person() {
    # Unauthorized
    curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -d '{"query": "{ persons { name title } }"}'

    # Login
    curl -X GET ${endpoint_app}token/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{ "username": "admin", "password", '${ADMIN_KEY}'"} }'
    
    # Authorized
    curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Carla\", title: \"PhD\") { name, title } }" }'
    
    # curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Pedro\", title: \"Undergraduate\") { name, title } }" }'
    
    # curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Zé\", title: \"Bocó\") { name, title } }" }'
    
    # curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "{ persons { name title } }"}'
    
    # curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { update(id: 1, name: \"Carla\", title: \"PhD Candidate\") { id, name, title } }" }'
    
    # curl -X POST ${endpoint_app}person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { delete(id: 2) }" }'
    
    # curl -X POST ${endpoint_app}person/ -H'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "{ persons { name title } }"}'
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

    deploy
    
    # --------------------------------------------------------------- #
    # Caso deseje criar a conta "admin", mas já foi criada no script  #
    # de inicialização do servidor PostgreSQL                         #
    # veja: `postgres/init/01-pm.sh`                                  #
    # Variáveis `ADMIN_KEY` e `ADMIN_SALT` foram criadas em `setup()` #
    # --------------------------------------------------------------- #
    # admin

    printf '\nexport authorization_token='$authorization_token
    printf '\nexport endpoint_app='${endpoint_app}'\n'

    person
    # resource
}

main
