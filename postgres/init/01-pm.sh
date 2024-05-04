#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER pmdb;
    CREATE DATABASE pmdb;
    ALTER DATABASE pmdb OWNER TO pmdb;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "ALTER ROLE pmdb WITH PASSWORD '$POSTGRES_PASSWORD';"
