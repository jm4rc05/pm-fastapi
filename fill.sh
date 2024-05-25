#!/bin/zsh

for i in {1..1000} do
    docker exec postgres psql -U pmdb -c "INSERT INTO person(name, title) VALUES('John Doe', 'N/A');"
done
