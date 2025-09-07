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

@app.get("/sql")
def test_db (sql: str, db: Session = Depends(get_db)):
  result = db.execute(
    # text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
    text(sql)
  )

  rows = result.fetchall() # list of Row
  # tables = [row[0] for row in rows] # 取第一欄 (tablename)

  # return { "tables": tables }

  print(rows)

  return { "msg": "good job" };

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
