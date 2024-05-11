from fastapi import Depends

from ariadne import load_schema_from_path, QueryType, MutationType, make_executable_schema
from graphql import GraphQLSchema

from db.session import SessionLocal
from db.model import Resource

from util.common import logger


def session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

query = QueryType()
mutation = MutationType()

resources_db = []

@query.field('resources')
def resources(*_):
    return resources_db

@mutation.field('add')
def add(_, info, name, description, db: SessionLocal = Depends(session)):
    resources_db.append({ 'name': name, 'description': description })
    return {'name': name, 'description': description }

def schema() -> GraphQLSchema:
    load_path = f'graphql/types/resource.graphql'
    defs = load_schema_from_path(load_path)
    return make_executable_schema(defs, [query, mutation])
