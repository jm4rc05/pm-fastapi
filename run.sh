#!/bin/zsh

# Cleanup
docker compose down --volumes
docker compose up --detach
echo 'Esperando a morte da bezerra...'
sleep 10

# Security
# API
export kms_api_key_value=$(openssl rand -hex 16) && echo KMS API Key: $kms_api_key_value
aws ssm put-parameter --name 'kms-api-key' --value ${kms_api_key_value} --type 'SecureString' --overwrite
# DB
export kms_db_key_value=$(openssl rand -hex 16) && echo KMS DB Key: $kms_db_key_value
aws ssm put-parameter --name 'kms-db-key' --value ${kms_db_key_value} --type 'SecureString' --overwrite

header='{"alg":"HS256","typ":"JWT"}' && payload='{"token": "'${kms_api_key_value}'"}' && encoded_header=$(echo -n "$header" | base64 | tr -d '=' | tr '/+' '_-') && encoded_payload=$(echo -n "$payload" | base64 | tr -d '=' | tr '/+' '_-') && header_payload="${encoded_header}.${encoded_payload}" && signature=$(echo -n "$header_payload" | openssl dgst -sha256 -hmac "${kms_api_key_value}" -binary | base64 | tr -d '=' | tr '/+' '_-')

export authorization_token="${header_payload}.${signature}" && echo Authorization token: $authorization_token

echo 'End point: '${authorization_token}

function person() {
    # Deploy/test person
    sls person:deploy --stage local && export endpoint_person=`aws lambda create-function-url-config --function-name person-local-api --auth-type NONE | jq -r '.FunctionUrl'`

    echo 'End point: '${endpoint_person}

    # Unauthorized
    curl -X POST ${endpoint_person}/person/ -H 'Content-Type: application/json' -d '{"query": "{ persons { name title } }"}'

    # Authorized
    curl -X POST ${endpoint_person}/person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Carla\", title: \"PhD\") { name, title } }" }'

    curl -X POST ${endpoint_person}/person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Pedro\", title: \"Undergraduate\") { name, title } }" }'

    curl -X POST ${endpoint_person}/person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Zé\", title: \"Bocó\") { name, title } }" }'

    curl -X POST ${endpoint_person}/person/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "{ persons { name title } }"}'
}

function resource() {
    # Deploy/test resource
    sls resource:deploy --stage local && export endpoint_resource=`aws lambda create-function-url-config --function-name resource-local-api --auth-type NONE | jq -r '.FunctionUrl'`

    echo 'End point: '${endpoint_resource}

    # Unauthorized
    curl -X POST ${endpoint_resource}/resource/ -H 'Content-Type: application/json' -d '{"query": "{ resources { name description } }"}'

    # Authorized
    curl -X POST ${endpoint_resource}/resource/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Sala90\", description: \"Sala de 90 lugares\") { name, description } }" }'

    curl -X POST ${endpoint_resource}/resource/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Lab90\", description: \"Laboratório de 90 bancadas\") { name, description } }" }'

    curl -X POST ${endpoint_resource}/resource/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "mutation { add(name: \"Aud90\", description: \"Auditório de 90 lugares\") { name, description } }" }'

    curl -X POST ${endpoint_resource}/resource/ -H 'Content-Type: application/json' -H 'Authorization: Bearer '${authorization_token} -d '{"query": "{ resources { name description } }"}'
}

person
# resource
