from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from redis import Redis
from rq import Queue
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
import os
import shutil

from . import models  # 要先 import，讓 SQLAlchemy 註冊到 Base
from .db import Base, engine, get_db
from .helper import short_uuid
# from .tasks import add_numbers

HOST = 'http://127.0.0.1:8000' # protocol + host.
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
  return { 'error': 0, 'message': 'Hello World' }

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

  return { 'error': 0, 'message': '', 'schema': schema }

# for dev
@app.get("/sql")
def test_db (sql: str, db: Session = Depends(get_db)):
  result = db.execute(
    text(sql)
  )

  if (sql[0:5].lower() == 'drop ' or
      sql[0:7].lower() == 'insert ' or
      sql[0:7].lower() == 'delete ' or
      sql[0:7].lower() == 'update '
  ):
    db.commit()

    return {
      'error': 1,
      'message': 'SQL executed.',
    }

  rows = {}

  for row in result.fetchall():
    print(row)

  return { 'error': 0, 'message': '', 'rows': rows };

# @app.post("/add")
# def add(a: int, b: int, db=Depends(get_db)):
#   # 投遞到 RQ queue
#   job = taskQueue.enqueue(add_numbers, a, b)
#   return {"job_id": job.get_id()}

@app.post("/upload")
async def upload (files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
  file_results = []
  files_to_insert = []

  for file in files:
    # === file extension check. ===

    ext = '.' + file.filename.split('.')[-1].lower()

    if ext != '.fcs':
      file_results.append({
        'download_url': '',
        'file': file.filename,
        'result': 'the extension is not .fcs',
      })

      continue

    # === file source check. ===

    content = await file.read(10)

    if not content.startswith(b"FCS"):
      file_results.append({
        'download_url': '',
        'file': file.filename,
        'result': 'not a real Flow Cytometry Standard(FCS) file.',
      })

      continue

    # === save the file. ===

    id = short_uuid()

    file_path = os.path.join(UPLOAD_DIR, id)

    with open(file_path, "wb") as buffer:
      shutil.copyfileobj(file.file, buffer)

    files_to_insert.append({
      'file_path': file_path,
      'id': id,
      'name': file.filename,
    })

    file_results.append({
      'download_url': HOST + '/download/' + id,
      'file': file.filename,
      'result': 'uploaded and saved.',
    })

  # record files.
  if len(files_to_insert) > 0:
    db.execute(
      text('INSERT INTO file (id, file_path, name) VALUES (:id, :file_path, :name);'),
      files_to_insert
    )

    db.commit()

  return {
    'error': 0,
    'message': '',
    'file_results': file_results,
  }

@app.get("/download/{file_id}")
def download (file_id: str, db: Session = Depends(get_db)):
  result = db.execute(
    text('SELECT file_path, name, uploader FROM file WHERE id = :id;'),
    { 'id': file_id }
  )

  rows = result.fetchall()

  if len(rows) < 1:
    raise HTTPException(
      status_code = 404,
      detail = {
        'error': -1,
        'message': 'no such file record.',
      }
    )

  file_path = rows[0][0]
  name = rows[0][1]
  uploader = rows[0][2]

  print(file_path, id, name, uploader)

  if not os.path.exists(file_path):
    raise HTTPException(
      status_code = 404,
      detail = {
        'error': -2,
        'message': 'file not existant.',
      }
    )

  if not os.path.exists(file_path):
    raise HTTPException(
      status_code = 404,
      detail = {
        'error': -2,
        'message': 'file not existant.',
      }
    )

  if uploader != None:
    raise HTTPException(
      status_code = 404,
      detail = {
        'error': -3,
        'message': 'can not download the file.',
      }
    )

  return FileResponse(
    path = file_path,
    filename = name, # 指定下載時顯示的檔名
    media_type = 'application/vnd.isac.fcs' # 通用二進位格式
  )
