from fastapi import Depends

from ariadne import load_schema_from_path, QueryType, MutationType, make_executable_schema
from graphql import GraphQLSchema

from db.session import SessionLocal
from db.model import Person

from util.common import logger


def session():
    db = SessionLocal()
    try:
        logger.info('*** OPEN ***')
        yield db
    finally:
        logger.info('*** CLOSE ***')
        db.close()

query = QueryType()
mutation = MutationType()

@query.field('person')
def person(_, name, db: SessionLocal = Depends(session)):
    return SessionLocal().query(Person).filter(Person.name == name).first()

@query.field('persons')
def persons(*_, db: SessionLocal = Depends(session)):
    return SessionLocal().query(Person).all()

@mutation.field('add')
def add(_, info, name, title, db: SessionLocal = Depends(session)):
    with SessionLocal.begin() as session:
        person = Person(name = name, title = title)
        session.add(person)
        session.commit()
        
    return {'name': name, 'title': title }

@mutation.field('update')
def update(_, info, name, title, db: SessionLocal = Depends(session)):
    with SessionLocal.begin() as session:
        query = SessionLocal().query(Person).filter(Person.name == name)
        person = query.first()
        person.title = title
        session.commit()
    
    return {'name': name, 'title': title }

@mutation.field('delete')
def delete(_, info, name, db: SessionLocal = Depends(session)):
    with SessionLocal.begin() as session:
        query = SessionLocal().query(Person).filter(Person.name == name)
        person = query.first()
        session.delete(person)
        session.commit()

    return {'message': f'{name} deleted'}

def schema() -> GraphQLSchema:
    load_path = 'types/person.graphql'
    defs = load_schema_from_path(load_path)
    return make_executable_schema(defs, [query, mutation])
