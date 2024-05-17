#!/bin/bash
set -e

psql -U "$POSTGRES_USER" <<-EOSQL
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
