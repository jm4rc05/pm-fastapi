from ariadne import load_schema_from_path, QueryType, MutationType, make_executable_schema
from graphql import GraphQLSchema

from api.db.database import session_factory
from api.db.models.resource import Resource

from api.util.common import logger


query = QueryType()
mutation = MutationType()

@query.field('resource')
def resource(_, id):
    db = session_factory()
    with db as db:
        return db.query(Resource).filter(Resource.id == id).first()

@query.field('resources')
async def resources(*_):
    db = session_factory()
    with db as db:
        return db.query(Resource).all()

@mutation.field('add')
async def add(_, info, name, description):
    _resource = Resource(name = name, description = description)
    db = session_factory()
    with db as db:
        db.add(_resource)
        db.commit()
        db.refresh(_resource)

        return _resource

def schema() -> GraphQLSchema:
    load_path = 'api/types/resource.graphql'
    defs = load_schema_from_path(load_path)
    return make_executable_schema(defs, [query, mutation])
