import os, logging
from fastapi import Request, Response
from ariadne import load_schema_from_path, QueryType, MutationType, make_executable_schema
from ariadne.asgi import GraphQL
from ariadne.validation import cost_validator, cost_directive
from sqlalchemy import select, Numeric
from sqlalchemy.orm import subqueryload, joinedload
from graphql import GraphQLSchema
from decouple import config
from dotenv import load_dotenv
from constants import ROOT_DIR
from api.db.database import session_factory
from api.db.models.sales import Category, Address, Shop, Customer, Product, Cart, Item


load_dotenv('.env.local')

API_MAXIMUM_COST = config('API_MAXIMUM_COST', cast = int, default = 5)
logging.info(f'API maximum cost: {API_MAXIMUM_COST}')

query = QueryType()
mutation = MutationType()


@query.field('category')
def category(_, __, id: int) -> Category:
    with session_factory() as db:
        return db.scalars(select(Category).filter(Category.id == id).options(subqueryload('*'))).first()

@query.field('categories')
def categories(*_):
    with session_factory() as db:
        return db.scalars(select(Category).options(subqueryload('*'))).all()

@query.field('address')
def address(_, __, id: int) -> Address:
    with session_factory() as db:
        return db.scalars(select(Address).filter(Address.id == id).options(subqueryload('*'))).first()

@query.field('shop')
def shop(_, __, id: int) -> Shop:
    with session_factory() as db:
        return db.scalars(select(Shop).filter(Shop.id == id).options(subqueryload('*'))).first()

@query.field('customer')
def customer(_, __, id: int) -> Customer:
    with session_factory() as db:
        return db.scalars(select(Customer).filter(Customer.id == id).options(subqueryload('*'))).first()

@query.field('product')
def product(_, __, id: int) -> Product:
    with session_factory() as db:
        return db.scalars(select(Product).filter(Product.id == id).options(subqueryload('*'))).first()

@query.field('cart')
def cart(_, __, id: int) -> Cart:
    with session_factory() as db:
        return db.scalars(select(Cart).filter(Cart.id == id).options(subqueryload('*'))).first()

@query.field('item')
def item(_, __, id: int) -> Item:
    with session_factory() as db:
        return db.scalars(select(Item).filter(Item.id == id).options(subqueryload('*'))).first()

@mutation.field('addCategory')
def addCategory(_, __, name: str) -> Category:
    with session_factory() as db:
        _category = Category(name = name)
        db.add(_category)
        db.commit()
        db.refresh(_category)
        logging.info(f'Added {__name__} {name}')

        return _category

@mutation.field('addAddress')
def addAddress(_, __, street: str, city: str, county: str, postal: str, country: str) -> Address:
    with session_factory() as db:
        _address = Address(street = street, city = city, county = county, postal = postal, country = country)
        db.add(_address)
        db.commit()
        db.refresh(_address)
        logging.info(f'Added {__name__} {street}/{city}')

        return _address

@mutation.field('addShop')
def addShop(_, __, name: str, category: int = None, address: int = None) -> Shop:
    with session_factory() as db:
        _shop = Shop(name = name)
        if category:
            _shop.category_id = category
        if address:
            _shop.address_id = address
        db.add(_shop)
        db.commit()
        db.refresh(_shop)
        logging.info(f'Added {__name__} {name}')

        return _shop

@mutation.field('addCustomer')
def addCustomer(_, __, name: str, category: int = None, address: int = None) -> Customer:
    with session_factory() as db:
        _customer = Customer(name = name)
        if category:
            _customer.category_id = category
        if address:
            _customer.address_id = address
        db.add(_customer)
        db.commit()
        db.refresh(_customer)
        logging.info(f'Added {__name__} {name}')

        return _customer

@mutation.field('addProduct')
def addProduct(_, __, name: str, price: Numeric) -> Product:
    with session_factory() as db:
        _product = Product(name = name, price = price)
        db.add(_product)
        db.commit()
        db.refresh(_product)
        logging.info(f'Added {__name__} {name}')
        
        return _product

@mutation.field('addCart')
def addCart(_, __, customer: int, shop: int) -> Cart:
    with session_factory() as db:
        _cart = Cart(customer_id = customer, shop_id = shop)
        db.add(_cart)
        db.commit()
        db.refresh(_cart)
        logging.info(f'Added {__name__}')

        return _cart

@mutation.field('addItem')
def addItem(_, __, cart: int, product: int, quantity: int) -> Item:
    with session_factory() as db:
        _product = db.scalars(select(Product).filter(Product.id == product)).first()
        if _product:
            _value = _product.price * quantity
            _item = Item(cart_id = cart, product_id = product, quantity = quantity, value = _value)
            db.add(_item)
            db.commit()
            db.refresh(_item)
            logging.info(f'Added {__name__}')
            id = _item.id
            _item = db.scalars(select(Item).filter(Item.id == id).options(subqueryload('*'))).first()

            return _item

@mutation.field('updateCategory')
def updateCategory(_, __, id: int, name: str = None) -> Category:
    with session_factory() as db:
        _category = db.scalars(select(Category).filter(Category.id == id)).first()
        if _category:
            if name:
                _category.name = name
            db.commit()
            db.refresh(_category)
            logging.info(f'Updated {__name__} {name}')
        
        return _category

@mutation.field('updateAddress')
def updateAddress(_, __, id: int, street: str = None, city: str = None, county: str = None, postal: str = None, country: str = None) -> Address:
    with session_factory() as db:
        _address = db.scalars(select(Address).filter(Address.id == id)).first()
        if _address:
            if street:
                _address.street = street
            if city:
                _address.city = city
            if county:
                _address.county = county
            if postal:
                _address.postal = postal
            if country:
                _address.country = country
            db.commit()
            db.refresh(_address)
            logging.info(f'Updated {__name__} {street}/{city}')

        return _address

@mutation.field('updateShop')
def updateShop(_, __, id: int, name: str = None, category: str = None, address: str = None) -> Shop:
    with session_factory() as db:
        _shop = db.scalars(select(Shop).filter(Shop.id == id)).first()
        if _shop:
            if name:
                _shop.name = name
            if category:
                _shop.category_id = category
            if address:
                _shop.address_id = address
            db.commit()
            db.refresh(_shop)
            logging.info(f'Updated {__name__} {name}')
        
        return _shop

@mutation.field('updateCustomer')
def updateCustomer(_, __, id: int, name: str = None, category: str = None, address: str = None) -> Customer:
    with session_factory() as db:
        _customer = db.scalars(select(Customer).filter(Customer.id == id)).first()
        if _customer:
            if name:
                _customer.name = name
            if category:
                _customer.category_id = category
            if address:
                _customer.address_id = address
            db.commit()
            db.refresh(_customer)
            logging.info(f'Updated {__name__} {name}')

        return _customer

@mutation.field('updateProduct')
def updateProduct(_, __, id: int, name: str = None, price: Numeric = None) -> Product:
    with session_factory() as db:
        _product = db.scalars(select(Product).filter(Product.id == id)).first()
        if _product:
            if name:
                _product.name = name
            if price:
                _product.price = price
            db.commit()
            db.refresh(_product)
            logging.info(f'Updated {__name__} {name}')
        
        return _product

@mutation.field('updateItem')
def updateItem(_, __, id: int, quantity: int = None, value: Numeric = None) -> Item:
    with session_factory() as db:
        _item = db.scalars(select(Item).filter(Item.id == id)).first()
        if _item:
            if quantity:
                _item.quantity = quantity
            if value:
                _item.value = value
            db.commit()
            db.refresh(_item)
            logging.info(f'Updated {__name__}')
        
        return _item

@mutation.field('deleteCategory')
def deleteCategory(_, __, id: int) -> bool:
    with session_factory() as db:
        _category = db.scalars(select(Category).filter(Category.id == id)).first()
        if _category:
            db.delete(_category)
            db.commit()
            logging.info(f'Deleted {__name__} {_category.name}')
            return True

        return False

@mutation.field('deleteAddress')
def deleteAddress(_, __, id: int) -> bool:
    with session_factory() as db:
        _address = db.scalars(select(Address).filter(Address.id == id)).first()
        if _address:
            db.delete(_address)
            db.commit()
            logging.info(f'Deleted {__name__} {_address.name}')
            return True
        
        return False

@mutation.field('deleteShop')
def deleteShop(_, __, id: int) -> bool:
    with session_factory() as db:
        _shop = db.scalars(select(Shop).filter(Shop.id == id)).first()
        if _shop:
            db.delete(_shop)
            db.commit()
            logging.info(f'Deleted {__name__} {_shop.name}')
            return True
        
        return False

@mutation.field('deleteCustomer')
def deleteCustomer(_, __, id: int) -> bool:
    with session_factory() as db:
        _customer = db.scalars(select(Customer).filter(Customer.id == id)).first()
        if _customer:
            db.delete(_customer)
            db.commit()
            logging.info(f'Deleted {__name__} {_customer.name}')
            return True
        
        return False

@mutation.field('deleteProduct')
def deleteProduct(_, __, id: int) -> bool:
    with session_factory() as db:
        _product = db.scalars(select(Product).filter(Product.id == id)).first()
        if _product:
            db.delete(_product)
            db.commit()
            logging.info(f'Deleted {__name__} {_product.name}')
            return True

        return False

@mutation.field('deleteItem')
def deleteItem(_, __, id: int) -> bool:
    with session_factory() as db:
        _item = db.scalars(select(Item).filter(Item.id == id)).first()
        if _item:
            db.delete(_item)
            db.commit()
            logging.info(f'Deleted {__name__}')
            return True

        return False

def serve(request: Request) -> Response:
    load_path = 'api/types/sales.graphql'
    defs = load_schema_from_path(load_path)
    schema = make_executable_schema(defs, query, mutation)
    return GraphQL(
        schema, 
        validation_rules = [ cost_validator(maximum_cost = API_MAXIMUM_COST) ],
        debug = True
    ).http_handler.graphql_http_server(request)
