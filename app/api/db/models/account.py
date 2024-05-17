from sqlalchemy import Column, Integer, String
from api.db.database import Base


class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    key = Column(String)
    salt = Column(String)
