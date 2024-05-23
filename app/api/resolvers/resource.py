from ariadne import load_schema_from_path, QueryType, MutationType, make_executable_schema
from graphql import GraphQLSchema
from api.db.database import session_factory
from api.db.models.resource import Resource


query = QueryType()
mutation = MutationType()

@query.field('resource')
def resource(_, id):
    with session_factory() as db:
        return db.query(Resource).filter(Resource.id == id).first()

@query.field('resources')
async def resources(*_):
    with session_factory() as db:
        return db.query(Resource).all()

@mutation.field('add')
async def add(_, __, name, description):
    _resource = Resource(name = name, description = description)
    with session_factory() as db:
        db.add(_resource)
        db.commit()
        db.refresh(_resource)

        return _resource

@mutation.field('update')
def update(_, __, id, name = None, description = None):
    with session_factory() as db:
        _resource = db.query(Resource).filter(Resource.id == id).first()
        if _resource:
            if name:
                _resource.name = name
            if description:
                _resource.description = description
            db.commit()
            db.refresh(_resource)
        
        return _resource

@mutation.field('delete')
def delete(_, __, id):
    with session_factory() as db:
        _resource = db.query(Resource).filter(Resource.id == id).first()
        if _resource:
            db.delete(_resource)
            db.commit()
            return True
        
        return False

def schema() -> GraphQLSchema:
    load_path = 'api/types/resource.graphql'
    defs = load_schema_from_path(load_path)
    return make_executable_schema(defs, [query, mutation])
