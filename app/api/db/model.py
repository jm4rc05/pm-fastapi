from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from session import engine


Base = declarative_base()

class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    title = Column(String)

class Resource(Base):
    __tablename__ = 'resource'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    description = Column(String)

Base.metadata.create_all(engine)
