#!/bin/bash

# Define variables

apt update -y
apt upgrade -y
apt install gnupg2 wget vim curl -y
sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
apt update -y
apt install postgresql postgresql-contrib
systemctl start postgresql
systemctl enable postgresql
