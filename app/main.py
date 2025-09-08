from datetime import datetime
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from redis import Redis
from rq import Queue
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import time

from . import models  # 要先 import，讓 SQLAlchemy 註冊到 Base
from .db import Base, engine, get_db
from .helper import log_action, seconds_to_text, short_uuid
# from .tasks import add_numbers

HOST = 'http://127.0.0.1:8000' # protocol + host.
UPLOAD_DIR = "uploaded_files"

app = FastAPI()

# Redis 連線 & Queue
redisConn = Redis(host = 'redis', port = 6379)

taskQueue = Queue('default', connection = redisConn)

os.makedirs(UPLOAD_DIR, exist_ok = True)

@app.on_event('startup')
def on_startup():
  Base.metadata.create_all(bind = engine)  # 不會刪資料，只會建立缺少的表

@app.get('/')
def read_root ():
  return { 'error': 0, 'message': 'Hello World' }

# for dev
@app.get('/dev/sqlSchema')
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
@app.get('/dev/sql')
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

@app.post('/upload')
async def upload (files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
  file_results = []
  files_to_insert = []
  start_time = time.time()

  for file in files:
    # === file extension check. ===

    ext = '.' + file.filename.split('.')[-1].lower()
    upload_time = datetime.now()

    if ext != '.fcs':
      file_results.append({
        'download_url': '',
        'file': file.filename,
        'file_size': 0,
        'result': 'the extension is not .fcs',
        'upload_time': upload_time,
      })

      continue

    # === file source check. ===

    content = await file.read() # 讀取整個檔案
    file_size = len(content)

    if file_size > (1024 * 1024 * 1000): # 1000MB
      file_results.append({
        'download_url': '',
        'file': file.filename,
        'file_size': file_size,
        'result': 'the file is bigger than 1000MB.',
        'upload_time': upload_time,
      })

      continue

    if not content.startswith(b'FCS'):
      file_results.append({
        'download_url': '',
        'file': file.filename,
        'file_size': file_size,
        'result': 'not a real Flow Cytometry Standard(FCS) file.',
        'upload_time': upload_time,
      })

      continue

    # === save the file. ===

    id = short_uuid()

    file_path = os.path.join(UPLOAD_DIR, id)

    with open(file_path, 'wb') as buffer:
      shutil.copyfileobj(file.file, buffer)

    files_to_insert.append({
      'file_path': file_path,
      'id': id,
      'name': file.filename,
    })

    file_results.append({
      'download_url': HOST + '/download/' + id,
      'file': file.filename,
      'file_size': file_size,
      'result': 'uploaded and saved.',
      'upload_time': upload_time,
    })

  # record files.
  if len(files_to_insert) > 0:
    db.execute(
      text('INSERT INTO file (id, file_path, name) VALUES (:id, :file_path, :name);'),
      files_to_insert
    )

    db.commit()

  log_action(
    db,
    '',
    'someone uploaded ' + str(len(files)) + ' files, duration: ' + str(time.time() - start_time)
  )

  return {
    'error': 0,
    'message': '',
    'file_results': file_results,
  }

@app.get('/download/{file_id}')
def download (file_id: str, db: Session = Depends(get_db)):
  result = db.execute(
    text('SELECT file_path, name, uploader_id FROM file WHERE id = :id;'),
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
  uploader_id = rows[0][2]

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

  if uploader_id != None:
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

# @app.post("/add")
# def add(a: int, b: int, db=Depends(get_db)):
#   # 投遞到 RQ queue
#   job = taskQueue.enqueue(add_numbers, a, b)
#   return {"job_id": job.get_id()}
