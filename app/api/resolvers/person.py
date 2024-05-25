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
from api.db.models.person import Person


load_dotenv('.env.local')

logging.config.fileConfig(f'{ROOT_DIR}/logging.conf')
logger = logging.getLogger()

API_MAXIMUM_COST = config('API_MAXIMUM_COST', cast = int, default = 5)
logger.info(f'API maximum cost: {API_MAXIMUM_COST}')

query = QueryType()
mutation = MutationType()

@query.field('person')
def person(_, id):
    with session_factory() as db:
        return db.query(Person).filter(Person.id == id).first()

@query.field('persons')
def persons(*_):
    with session_factory() as db:
        return db.query(Person).all()

@mutation.field('add')
def add(_, __, name, title):
    _person = Person(name = name, title = title)
    with session_factory() as db:
        db.add(_person)
        db.commit()
        db.refresh(_person)
        logger.info(f'Added {__name__} {name}')
    
    return _person

@mutation.field('update')
def update(_, __, id, name = None, title = None):
    with session_factory() as db:
        _person = db.query(Person).filter(Person.id == id).first()
        if _person:
            if name:
                _person.name = name
            if title:
                _person.title = title
            db.commit()
            db.refresh(_person)
            logger.info(f'Updated {__name__} {name}')
        
        return _person

@mutation.field('delete')
def delete(_, __, id):
    with session_factory() as db:
        _person = db.query(Person).filter(Person.id == id).first()
        if _person:
            db.delete(_person)
            db.commit()
            logger.info(f'Deleted {__name__} {_person.name}')
            return True
        
        return False

def serve(request: Request) -> Response:
    load_path = 'api/types/person.graphql'
    defs = load_schema_from_path(load_path)
    schema = make_executable_schema(defs, [query, mutation])
    return GraphQL(
        schema, 
        logger = logging.Logger, 
        validation_rules = [ cost_validator(maximum_cost = API_MAXIMUM_COST) ],
        debug = True
    ).http_handler.graphql_http_server(request)
