#!/bin/bash
set -e

function hash() {
    openssl passwd -5 -salt $2 $1 | awk '{print $1}'
}

export password=$(hash "$ADMIN_KEY" "$ADMIN_SALT")

psql -U "$POSTGRES_USER" <<-EOSQL
    CREATE USER pmdb;
    CREATE DATABASE pmdb;
    ALTER DATABASE pmdb OWNER TO pmdb;
    ALTER ROLE pmdb WITH PASSWORD 'pmdb';
EOSQL
