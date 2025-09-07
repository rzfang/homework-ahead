from fastapi import Depends, FastAPI, File, UploadFile
from redis import Redis
from rq import Queue
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
import os
import shutil

from . import models  # 要先 import，讓 SQLAlchemy 註冊到 Base
from .db import Base, engine, get_db
# from .tasks import add_numbers

UPLOAD_DIR = "uploaded_files"
app = FastAPI()

# Redis 連線 & Queue
redisConn = Redis(host = "redis", port = 6379)

taskQueue = Queue("default", connection = redisConn)

os.makedirs(UPLOAD_DIR, exist_ok = True)

@app.on_event("startup")
def on_startup():
  Base.metadata.create_all(bind = engine)  # 不會刪資料，只會建立缺少的表

@app.get("/")
def read_root ():
  return { "msg": "Hello World" }

# for dev
@app.get("/sqlSchema")
def read_root (db: Session = Depends(get_db)):
  result = db.execute(
    text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
  )

  schema = {}

  rows = result.fetchall()

  for row in rows:
    tableName = row[0]

    result = db.execute(
      text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = :tableName;"),
      { 'tableName': tableName }
    )

    rows = result.fetchall()

    schema[tableName] = [row[0] for row in rows]

  return { 'schema': schema }

# for dev
@app.get("/sql")
def test_db (sql: str, db: Session = Depends(get_db)):
  result = db.execute(
    text(sql)
  )

  if sql[0:5].lower() =='drop ':
    print(result)

    return {
      'error': 1,
      'message': 'dropped.',
    }

  rows = result.fetchall() # list of Row

  return { "msg": rows };

# @app.post("/add")
# def add(a: int, b: int, db=Depends(get_db)):
#   # 投遞到 RQ queue
#   job = taskQueue.enqueue(add_numbers, a, b)
#   return {"job_id": job.get_id()}

@app.post("/upload")
def upload (files: List[UploadFile] = File(...)):
  savedFiles = []

  for file in files:
    filePath = os.path.join(UPLOAD_DIR, file.filename)

    with open(filePath, "wb") as buffer:
      shutil.copyfileobj(file.file, buffer)

    savedFiles.append(filePath)

  return { "savedFiles": savedFiles }
