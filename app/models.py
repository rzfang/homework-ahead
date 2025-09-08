from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship

from .db import Base

class Users (Base):
  __tablename__ = 'users' # "user" is reserved word in PostgreSQL, use 'users' instead.
  id = Column(String, primary_key = True)
  email = Column(String, index = True, nullable = False)
  join_time = Column(DateTime, nullable = False, server_default = func.now())
  name = Column(String)

class File (Base):
  __tablename__ = 'file'
  id = Column(String, primary_key = True)
  create_time = Column(DateTime, nullable = False, server_default = func.now())
  file_path = Column(String, nullable = False)
  name = Column(String, nullable = False)
  uploader_id = Column(String, ForeignKey('users.id'))
  # users = relationship("Users")

class ActionLog (Base):
  __tablename__ = 'action_log'
  id = Column(Integer, primary_key = True, autoincrement=True)
  create_time = Column(DateTime, nullable = False, server_default = func.now())
  description = Column(String)
  user_id = Column(String, ForeignKey('users.id'))
