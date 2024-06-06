import logging
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.db.database import Base, session_factory
from pydantic import BaseModel
from typing import List
from passlib.context import CryptContext
from passlib.exc import UnknownHashError


context = CryptContext(schemes = ['sha256_crypt'])

profile = Table(
    'profile',
    Base.metadata,
    Column('role', ForeignKey('role.id'), primary_key = True),
    Column('account', ForeignKey('account.id'), primary_key = True)
)

class Account(Base):
    __tablename__ = 'account'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    name = Column(String)
    key = Column(String)
    salt = Column(String)
    roles: Mapped[List['Role']] = relationship(secondary = profile, back_populates = 'accounts')

class Role(Base):
    __tablename__ = 'role'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    name = Column(String)
    accounts: Mapped[List['Account']] = relationship(secondary = profile, back_populates = 'roles')

class Token(BaseModel):
    token: str
    type: str
