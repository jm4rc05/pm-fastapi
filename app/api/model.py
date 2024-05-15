from sqlalchemy import Column, Integer, String

from api.database import Base


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
