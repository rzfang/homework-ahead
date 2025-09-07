# homework-ahead
homework for AHEAD

# Tech Stack
- [Python](https://www.python.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [RQ](https://python-rq.org/)
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

# Develop

## Start the server

build and start the whole system.
```sh
$ docker compose up --build
```

## Refresh Db and start the server

refresh Db schema by giving up old Db data.
```sh
$ docker compose down -v
$ docker compose up --build
```

## API playground

after starting the server, access follow url to access API dashboard.
http://127.0.0.1:8000/docs#/default
