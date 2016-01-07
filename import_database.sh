#!/bin/bash

# Import data into local mysql database on Travis CI

echo "Downloading omegawiki-lexical.sql.gz"
mkdir -p cache
cd cache/
if [ ! -f omegawiki-lexical.sql ] ; then
  wget -q -c "http://www.omegawiki.org/downloads/omegawiki-lexical.sql.gz"
  gunzip omegawiki-lexical.sql.gz
fi
file omegawiki-lexical.sql

echo "Creating database and importing omegawiki-lexical.sql"
echo "create database omega" | mysql -u root
mysql omega -u root -h 127.0.0.1 < omegawiki-lexical.sql

cd ..
find cache/
