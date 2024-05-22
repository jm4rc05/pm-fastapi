from sqlalchemy import Column, Integer, String
from api.db.database import Base
from pydantic import BaseModel
from typing import Union


class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    key = Column(String)
    salt = Column(String)

class Token(BaseModel):
    token: str
    type: str

class TokenData(BaseModel):
    username: Union[str, None] = None
