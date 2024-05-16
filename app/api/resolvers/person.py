from ariadne import load_schema_from_path, QueryType, MutationType, make_executable_schema
from graphql import GraphQLSchema

from api.db.database import session_factory
from api.db.models.person import Person

from api.util.common import logger


query = QueryType()
mutation = MutationType()

@query.field('person')
def person(_, id):
    db = session_factory()
    with db as db:
        return db.query(Person).filter(Person.id == id).first()

@query.field('persons')
def persons(*_):
    db = session_factory()
    with db as db:
        return db.query(Person).all()

@mutation.field('add')
def add(_, info, name, title):
    _person = Person(name = name, title = title)
    # db = session_factory()
    with session_factory() as db:
        db.add(_person)
        db.commit()
        db.refresh(_person)
    
    return _person

@mutation.field('update')
def update(_, info, id, name = None, title = None):
    db = session_factory()
    with db as db:
        _person = db.query(Person).filter(Person.id == id).first()
        if _person:
            if name:
                _person.name = name
            if title:
                _person.title = title
            db.commit()
            db.refresh(_person)
        
        return _person

@mutation.field('delete')
def delete(_, info, name):
    db = session_factory()
    with db as db:
        _person = db.query(Person).filter(Person.id == id).first()
        if _person:
            db.delete(_person)
            db.commit()
            return True
        
        return False

def schema() -> GraphQLSchema:
    load_path = 'api/types/person.graphql'
    defs = load_schema_from_path(load_path)
    return make_executable_schema(defs, [query, mutation])
