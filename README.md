# Quart MySQL Boilerplate

This is a boilerplate for a Quart app that can run as a pipenv, Heroku or Docker application. Requires `python 3.7`.

## Local MySQL server

- Create the application user and password:
  - Logon to MySQL using root user
  - Create the counter database `CREATE DATABASE counter;`
  - Create the counter user `CREATE USER 'counter_user'@'%' IDENTIFIED BY 'counter_password';`
  - Give privileges to counter user `GRANT ALL PRIVILEGES ON counter.* TO 'counter_user'@'%';` and `FLUSH PRIVILEGES;`
- Install pipenv if you don't have it using `pip install pipenv`
- Install the packages: `pipenv install`
- Run the first migration with `pipenv run alembic upgrade head`
  - Subsequent migrations after models changes can be run with `pipenv run alembic revision --autogenerate -m "added counter table field"` with [some caveats](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).
- Run `pipenv run quart run`
- Open `http://localhost:5000` on your browser
- To open a shell, just do `pipenv run quart shell`
- Run tests by doing `pipenv run pytest`

## Using Docker

- Add the path where this code lives on the Docker client
- Run `docker-compose up`
- In a new terminal or tab run:
  - `docker exec -it counterappmysql_web_1 alembic upgrade head` to initialize migrations
- Open `http://localhost:5000` on your browser
- Run tests by doing `docker exec -it counterappmysql_web_1 pytest`

## Production

- Use Hypercorn `hypercorn --bind 0.0.0.0:$PORT --reload wsgi:app`
