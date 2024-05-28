from typing import List
from sqlalchemy import Column, Integer, Numeric, String, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.db.database import Base


class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    name = Column(String)
    price = Column(Numeric(10, 2))

class Cart(Base):
    __tablename__ = 'cart'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    items: Mapped[List['Item']] = relationship()

class Item(Base):
    __tablename__ = 'item'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    cart: Mapped[int] = mapped_column(ForeignKey('cart.id'))
    product: Mapped[int] = mapped_column(ForeignKey('product.id'))
    quantity = Column(Integer)
    value = Column(Numeric(10, 2))
