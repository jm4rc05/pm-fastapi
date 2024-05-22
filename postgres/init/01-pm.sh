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

psql -U "pmdb" -d "pmdb" <<-EOSQL
    CREATE TABLE "public"."account" ( 
        "id" SERIAL,
        "name" VARCHAR UNIQUE NOT NULL,
        "key" VARCHAR NOT NULL,
        "salt" VARCHAR NOT NULL,
        CONSTRAINT "account_pkey" PRIMARY KEY ("id")
    );
    CREATE INDEX "ix_account_id" ON "public"."account" (
        "id" ASC
    );
    INSERT INTO "public"."account" (
        "name", 
        "key",
        "salt"
    ) VALUES (
        'admin', 
        '$password',
        '$ADMIN_SALT'
    );
EOSQL
