rm -f ./uploads/*;
rm -f ./extracted/*;
rm -f /tmp/1;

export PGPASSWORD=postgres;
psql -h localhost -U postgres -c "drop database firmware;"
psql -h localhost -U postgres -c "create database firmware;"

python ./manage.py migrate;
python ./manage.py runserver 0.0.0.0:10025;
