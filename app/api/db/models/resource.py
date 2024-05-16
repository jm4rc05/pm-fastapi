from sqlalchemy import Column, Integer, String

from api.db.database import Base


class Resource(Base):
    __tablename__ = 'resource'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    description = Column(String)
