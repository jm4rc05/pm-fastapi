from fastapi import Depends

from sqlalchemy.orm import Session

from ariadne import load_schema_from_path, QueryType, MutationType, make_executable_schema
from graphql import GraphQLSchema

from api.database import session_factory
from api.model import Person

from api.util.common import logger


query = QueryType()
mutation = MutationType()

@query.field('person')
def person(_, info, id):
    db: Session = session_factory()
    return db.query(Person).filter(Person.id == id).first()

@query.field('persons')
def persons(*_, info):
    db: Session = session_factory()
    return db.query(Person).all()

@mutation.field('add')
def add(_, info, name, title):
    db: Session = session_factory()
    _person = Person(name = name, title = title)
    db.add(_person)
    db.commit()
    db.refresh(_person)
    
    return _person

@mutation.field('update')
def update(_, info, id, name = None, title = None):
    db: Session = session_factory()
    _person = db.query(Person).filter(Person.id == id).first()
    if _person:
        if name:
            _person.name = name
        if description:
            _person.description = description
        db.commit()
        db.refresh(_person)
    
    return _person

@mutation.field('delete')
def delete(_, info, name):
    db: Session = session_factory()
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
