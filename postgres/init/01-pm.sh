#!/bin/bash
set -e

psql -U "$POSTGRES_USER" <<-EOSQL
    CREATE USER pmdb;
    CREATE DATABASE pmdb;
    ALTER DATABASE pmdb OWNER TO pmdb;
    ALTER ROLE pmdb WITH PASSWORD 'pmdb';
EOSQL

psql -U "pmdb" -d "pmbd" <<-EOSQL
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
        '$ADMIN_KEY',
        '$ADMIN_SALT'
    );
EOSQL
