from typing import List, Optional
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.db.database import Base


categorization = Table(
    'categorization',
    Base.metadata,
    Column('shop', ForeignKey('shop.id'), primary_key = True),
    Column('customer', ForeignKey('customer.id'), primary_key = True)
)

class Customer(Base):
    __tablename__ = 'customer'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    name = Column(String)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey('category.id'))
    category: Mapped[Optional['Category']] = relationship(back_populates = 'customers')
    address: Mapped[Optional[int]] = mapped_column(ForeignKey('address.id'))
    shops: Mapped[List['Shop']] = relationship(secondary = categorization, back_populates = 'customers')

class Shop(Base):
    __tablename__ = 'shop'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    name = Column(String)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey('category.id'))
    category: Mapped[Optional['Category']] = relationship(back_populates = 'shops')
    address: Mapped[Optional[int]] = mapped_column(ForeignKey('address.id'))
    customers: Mapped[List['Customer']] = relationship(secondary = categorization, back_populates = 'shops')

class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    name = Column(String)
    customers: Mapped[List['Customer']] = relationship(back_populates = 'category')
    shops: Mapped[List['Shop']] = relationship(back_populates = 'category')

class Address(Base):
    __tablename__ = 'address'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    street = Column(String)
    city = Column(String)
    county = Column(String)
    postal = Column(String)
    country = Column(String)
    customers: Mapped[List['Customer']] = relationship()
    shops: Mapped[List['Shop']] = relationship()
