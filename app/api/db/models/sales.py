from typing import List, Optional
from sqlalchemy import Column, Integer, Numeric, String, Table, ForeignKey
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
    address_id: Mapped[Optional[int]] = mapped_column(ForeignKey('address.id'))
    address: Mapped[Optional['Address']] = relationship(back_populates = 'customers')
    shops: Mapped[List['Shop']] = relationship(secondary = categorization, back_populates = 'customers')
    orders: Mapped[List['Cart']] = relationship(back_populates = 'customer')

class Shop(Base):
    __tablename__ = 'shop'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    name = Column(String)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey('category.id'))
    category: Mapped[Optional['Category']] = relationship(back_populates = 'shops')
    address_id: Mapped[Optional[int]] = mapped_column(ForeignKey('address.id'))
    address: Mapped[Optional['Address']] = relationship(back_populates = 'shops')
    customers: Mapped[List['Customer']] = relationship(secondary = categorization, back_populates = 'shops')
    sales: Mapped[List['Cart']] = relationship(back_populates = 'shop')

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

class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    name = Column(String)
    price = Column(Numeric(10, 2))
    orders: Mapped[List['Item']] = relationship()

class Cart(Base):
    __tablename__ = 'cart'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customer.id'))
    customer: Mapped['Customer'] = relationship(back_populates = 'orders')
    shop_id: Mapped[int] = mapped_column(ForeignKey('shop.id'))
    shop: Mapped['Shop'] = relationship(back_populates = 'sales')
    items: Mapped[List['Item']] = relationship()

class Item(Base):
    __tablename__ = 'item'

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    cart_id: Mapped[int] = mapped_column(ForeignKey('cart.id'))
    cart: Mapped['Cart'] = relationship(back_populates = 'items')
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id'))
    product: Mapped['Product'] = relationship(back_populates = 'orders')
    quantity = Column(Integer)
    value = Column(Numeric(10, 2))
