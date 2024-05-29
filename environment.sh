#!/bin/zsh

function main() {
    cat .env.local > .workspace.env
    echo 'POSTGRES_HOST=localhost' >> .workspace.env
    echo 'REDIS_HOST=localhost' >> .workspace.env
    echo 'API_TOKEN_DURATION=1000' >> .workspace.env
    echo 'API_LIMITER_RATE=100' >> .workspace.env
    echo 'API_MAXIMUM_COST=1' >> .workspace.env
}

main
