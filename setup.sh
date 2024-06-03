#!/bin/zsh

function main() {
    echo 'ADMIN_KEY='$(openssl rand -hex 32) > .env.local
    echo 'ADMIN_SALT='$(openssl rand -hex 16) >> .env.local
    
    ./environment.sh

    pipenv lock && pipenv requirements > requirements.txt

    # Cleanup - recria os containers
    docker compose down --volumes
    docker rmi app/api:latest
    docker compose up --detach

    docker logs app --follow
}

main
