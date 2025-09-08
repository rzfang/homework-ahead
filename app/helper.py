from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
import base64
import uuid

def seconds_to_text (time: int):
  hours = int(time / (60 * 60))
  minutes = int(time % (60 * 60) / 60)
  seconds = int(time % (60 * 60) % 60)

  if hours > 0:
    return str(hours).zfill(2) + 'h ' + str(minutes).zfill(2) + 'm ' + str(seconds).zfill(2) + 's'

  if minutes > 0:
    return str(minutes).zfill(2) + 'm ' + str(seconds).zfill(2) + 's'

  return str(seconds).zfill(2) + ' seconds'

def short_uuid ():
  return base64.urlsafe_b64encode(uuid.uuid4().bytes).rstrip(b'=').decode('ascii')

def log_action (db: Session, user_id: str, description: str):
  if user_id == '':
    user_id = None

  db.execute(
    text('INSERT INTO action_log (user_id, description) VALUES (:user_id, :description)'),
    {
      'user_id': user_id,
      'description': description,
    }
  )

  db.commit()
