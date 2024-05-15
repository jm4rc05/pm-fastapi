from fastapi import Depends

from sqlalchemy.orm import Session

from ariadne import load_schema_from_path, QueryType, MutationType, make_executable_schema
from graphql import GraphQLSchema

from api.database import session_factory
from api.model import Resource

from api.util.common import logger


query = QueryType()
mutation = MutationType()

@query.field('resource')
def resource(_, info, id):
    db: Session = session_factory()
    return db.query(Resource).filter(Resource.id == id).first()

@query.field('resources')
async def resources(*_):
    db: Session = session_factory()
    return db.query(Person).all()

@mutation.field('add')
async def add(_, info, name, description):
    db: Session = session_factory()
    _resource = Resource(name = name, description = description)
    db.add(_resource)
    db.commit()
    db.refresh(_resource)

    return _resource

def schema() -> GraphQLSchema:
    load_path = 'api/types/resource.graphql'
    defs = load_schema_from_path(load_path)
    return make_executable_schema(defs, [query, mutation])
