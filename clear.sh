#!/bin/zsh

docker exec postgres psql -U pmdb -c 'DELETE FROM person; ALTER SEQUENCE person_id_seq RESTART WITH 1;'
