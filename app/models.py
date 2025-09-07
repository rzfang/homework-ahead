from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .db import Base

class User(Base):
  __tablename__ = "user"
  id = Column(Integer, primary_key = True, index = True)
  name = Column(String, unique = True, index = True)

class Files(Base):
  __tablename__ = "file"
  id = Column(Integer, primary_key = True, index = True)
  name = Column(String)
  createTime = Column(DateTime, default = datetime.now())
  uploader = Column(Integer, ForeignKey("user.id"))
  user = relationship("User")