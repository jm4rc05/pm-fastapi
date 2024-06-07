#!/bin/zsh
set -e

function hash() {
    openssl passwd -5 -salt $2 $1 | awk '{print $1}'
}

function main() {

    set -a
    source .env.local
    set +a

    export password=$(hash "$ADMIN_KEY" "$ADMIN_SALT")
    
    cp accounts.template.sql accounts.sql
    sed -i '' -e 's#@PASSWORD#'$password'#g' accounts.sql
    sed -i '' -e 's#@SALT#'$ADMIN_SALT'#g' accounts.sql

    docker cp accounts.sql postgres:accounts.sql
    docker exec postgres bash -c 'psql -U "pmdb" -d "pmdb" -f "accounts.sql"'

}

main
