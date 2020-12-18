# Quart Feed

The FriendFeed clone using Quart.

## Local MySQL server

- Create the application user and password:
  - Logon to MySQL using root user
  - Create the counter database `CREATE DATABASE quartfeed;`
  - Create the counter user `CREATE USER 'quartfeed_user'@'%' IDENTIFIED BY 'quartfeed_password';`
  - Give privileges to counter user `GRANT ALL PRIVILEGES ON quartfeed.* TO 'quartfeed_user'@'%';` and `FLUSH PRIVILEGES;`
- Install the packages: `python -m pipenv install`
- Run the first migration with `python -m pipenv run alembic upgrade head`
  - Subsequent migrations after models changes can be run with `python -m pipenv run alembic revision --autogenerate -m "added new table field"` with [some caveats](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).
- Run `python -m pipenv run quart run`
- Open `http://localhost:5000` on your browser
- To open a shell, just do `python -m pipenv run quart shell`
- Run tests by doing `python -m pipenv run pytest`

## Using Docker

- Add the path where this code lives on the Docker client
- Run `docker-compose up --build`
- In a new terminal or tab run:
  - `docker-compose run --rm web pipenv run alembic upgrade head` to initialize migrations
- Open `http://localhost:5000` on your browser
- Run tests by doing `docker-compose run --rm web pipenv run pytest -s`
- Changes to the models, do `docker-compose run --rm web pipenv run alembic revision --autogenerate -m "added new table field"` and then `docker-compose run --rm web pipenv run alembic upgrade head`

## Production

- Use Hypercorn `hypercorn --bind 0.0.0.0:$PORT --reload wsgi:app`
