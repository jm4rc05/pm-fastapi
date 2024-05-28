import os, logging, logging.config
from fastapi import Request, Response
from ariadne import load_schema_from_path, QueryType, MutationType, make_executable_schema
from ariadne.asgi import GraphQL
from ariadne.validation import cost_validator, cost_directive
from graphql import GraphQLSchema
from decouple import config
from dotenv import load_dotenv
from constants import ROOT_DIR
from api.db.database import session_factory
from api.db.models.sales import Category, Address, Shop, Customer


load_dotenv('.env.local')

logging.config.fileConfig(f'{ROOT_DIR}/logging.conf')
logger = logging.getLogger('graphql')

API_MAXIMUM_COST = config('API_MAXIMUM_COST', cast = int, default = 5)
logger.info(f'API maximum cost: {API_MAXIMUM_COST}')

query = QueryType()
mutation = MutationType()

@query.field('category')
def category(_, id):
    with session_factory() as db:
        return db.query(Category).filter(Category.id == id).first()

@query.field('address')
def shop(_, id):
    with session_factory() as db:
        return db.query(Address).filter(Address.id == id).first()

@query.field('shop')
def shop(_, id):
    with session_factory() as db:
        return db.query(Shop).filter(Shop.id == id).first()

@query.field('customer')
def shop(_, id):
    with session_factory() as db:
        return db.query(Customer).filter(Customer.id == id).first()

@mutation.field('addCategory')
def addCategory(_, __, name):
    with session_factory() as db:
        _category = Category(name = name)
        db.add(_category)
        db.commit()
        db.refresh(_category)
        logger.info(f'Added {__name__} {name}')

        return _category

@mutation.field('addAddress')
def addAddress(_, __, street, city, county, postal, country):
    with session_factory() as db:
        _address = Address(street = street, city = city, county = county, postal = postal, country = country)
        db.add(_address)
        db.commit()
        db.refresh(_address)
        logger.info(f'Added {__name__} {street}/{city}')

        return _address

@mutation.field('addShop')
def addShop(_, __, name):
    with session_factory() as db:
        _shop = Shop(name = name)
        db.add(_shop)
        db.commit()
        db.refresh(_shop)
        logger.info(f'Added {__name__} {name}')

        return _shop

@mutation.field('addCustomer')
def addCustomer(_, __, name):
    with session_factory() as db:
        _customer = Customer(name = name)
        db.add(_customer)
        db.commit()
        db.refresh(_customer)
        logger.info(f'Added {__name__} {name}')

        return _customer

@mutation.field('updateCategory')
def updateCategory(_, __, id, name = None):
    with session_factory() as db:
        _category = db.query(Category).filter(Category.id == id).first()
        if _category:
            if name:
                _category.name = name
            db.commit()
            db.refresh(_category)
            logger.info(f'Updated {__name__} {name}')
        
        return _category

@mutation.field('updateAddress')
def updateAddress(_, __, id, street = None, city = None, county = None, postal = None, country = None):
    with session_factory() as db:
        _address = db.query(Address).filter(Address.id == id).first()
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
            logger.info(f'Updated {__name__} {street}/{city}')

        return _address

@mutation.field('updateShop')
def updateShop(_, __, id, name = None, category: int = None, address: int = None):
    with session_factory() as db:
        _shop = db.query(Shop).filter(Shop.id == id).first()
        if _shop:
            if name:
                _shop.name = name
            db.commit()
            db.refresh(_shop)
            logger.info(f'Updated {__name__} {name}')
        
        return _shop

@mutation.field('updateCustomer')
def updateCustomer(_, __, id, name = None, category: int = None, address: int = None):
    with session_factory() as db:
        _customer = db.query(Customer).filter(Customer.id == id).first()
        if _customer:
            if name:
                _customer.name = name
            db.commit()
            db.refresh(_customer)
            logger.info(f'Updated {__name__} {name}')

        return _customer

@mutation.field('deleteCategory')
def deleteCategory(_, __, id):
    with session_factory() as db:
        _category = db.query(Category).filter(Category.id == id).first()
        if _category:
            db.delete(_category)
            db.commit()
            logger.info(f'Deleted {__name__} {_category.name}')
            return True

        return False

@mutation.field('deleteAddress')
def deleteAddress(_, __, id):
    with session_factory() as db:
        _address = db.query(Address).filter(Address.id == id).first()
        if _address:
            db.delete(_address)
            db.commit()
            logger.info(f'Deleted {__name__} {_address.name}')
            return True
        
        return False

@mutation.field('deleteShop')
def deleteShop(_, __, id):
    with session_factory() as db:
        _shop = db.query(Shop).filter(Shop.id == id).first()
        if _shop:
            db.delete(_shop)
            db.commit()
            logger.info(f'Deleted {__name__} {_shop.name}')
            return True
        
        return False

@mutation.field('deleteCustomer')
def deleteCustomer(_, __, id):
    with session_factory() as db:
        _customer = db.query(Customer).filter(Customer.id == id).first()
        if _customer:
            db.delete(_customer)
            db.commit()
            logger.info(f'Deleted {__name__} {_customer.name}')
            return True
        
        return False

def serve(request: Request) -> Response:
    load_path = 'api/types/sales.graphql'
    defs = load_schema_from_path(load_path)
    schema = make_executable_schema(defs, [query, mutation])
    return GraphQL(
        schema, 
        logger = logging.Logger('root'), 
        validation_rules = [ cost_validator(maximum_cost = API_MAXIMUM_COST) ],
        debug = True
    ).http_handler.graphql_http_server(request)
