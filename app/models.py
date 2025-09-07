from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship

from .db import Base

class Users(Base):
  __tablename__ = "users" # "user" is reserved word in PostgreSQL, use 'users' instead.
  id = Column(String, primary_key = True)
  email = Column(String, index = True, nullable = False)
  join_time = Column(DateTime, default = datetime.now, nullable = False)
  name = Column(String, default = '')

class File(Base):
  __tablename__ = "file"
  id = Column(String, primary_key = True)
  create_time = Column(DateTime, default = datetime.now, nullable = False)
  name = Column(String, nullable = False)
  uploader = Column(String, ForeignKey("users.id"))
  # users = relationship("Users")
