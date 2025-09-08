# homework-ahead

## Progress
- US-MVP-001: 簡單檔案上傳 - ✅ Finshed.
- US-MVP-002: 私人檔案上傳 - 🛠️ In Progress.
- US-MVP-003: 簡單背景任務 - 📋 To Do.

## Verify

### US-MVP-001: 簡單檔案上傳

Refer to [API playground chapter](#api-playground) to use API test board.  
1. test `/upload`. it can help upload files and respond the download url of each file.  
2. test `/download/{file_id}`. visit the url with the file_id or visit the url directly from 1. , that will download the file.  

# Tech Stack
- [Python](https://www.python.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [RQ](https://python-rq.org/)
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

# Develop

## Dev Env set up

in the Linux, Mac OSX, clone the github repositry
```sh
$ git clone git@github.com:rzfang/homework-ahead.git
$ cd homework-ahead
```

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

### Know issue
everytime run refresh and start will go with FastAPI server error,  
it is because FastAPI depends on Db ready, but start a new Db take more time.  
**Short-term solution** is end run and restart again, since Db is not new, it catches up FastAPI.

## API playground

after starting the server, access following url to access API test board.  
http://127.0.0.1:8000/docs#/default


### APIs for development
- http://127.0.0.1:8000/dev/schema - to get Db tables with columns. to help to know Db.
- http://127.0.0.1:8000/dev/sql - to run the given SQL. **BE CAREFUL**, it can hurt Db directly.
