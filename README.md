# homework-ahead
homework for AHEAD

# Develop
build and start the whole system.
```sh
$ docker compose up --build
```

refresh Db schema by giving up old Db data.
```sh
$ docker compose down -v
$ docker compose up --build
```
