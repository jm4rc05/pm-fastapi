#!/bin/zsh
set -e

function main() {

    echo 'ADMIN_KEY='$(openssl rand -hex 32) > .env.local
    echo 'ADMIN_SALT='$(openssl rand -hex 16) >> .env.local
    
    cat .env.local > .workspace.env
    echo 'POSTGRES_HOST=localhost' >> .workspace.env
    echo 'REDIS_HOST=localhost' >> .workspace.env
    echo 'API_TOKEN_DURATION=10' >> .workspace.env
    echo 'API_LIMITER_RATE=100' >> .workspace.env
    echo 'API_MAXIMUM_COST=5' >> .workspace.env

    pipenv lock && pipenv requirements > requirements.txt

    # Cleanup - recria os containers
    docker compose down --volumes
    docker rmi app/api:latest
    docker compose up --detach

    docker logs app --follow

}

main
