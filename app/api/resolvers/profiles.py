import os, logging
from fastapi import Request, Response
from ariadne import load_schema_from_path, QueryType, make_executable_schema
from ariadne.asgi import GraphQL
from ariadne.validation import cost_validator, cost_directive
from sqlalchemy import select, Numeric
from sqlalchemy.orm import subqueryload, joinedload
from graphql import GraphQLSchema
from decouple import config
from dotenv import load_dotenv
from api.db.database import session_factory
from api.db.models.account import Account, Role


load_dotenv('.env.local')

query = QueryType()


@query.field('account')
def profile(_, __, id: int) -> Account:
    with session_factory() as db:
        return db.scalars(select(Account).filter(Account.id == id).options(subqueryload('*'))).first()

@query.field('role')
def role(_, __, id: int) -> Role:
    with session_factory() as db:
        return db.scalars(select(Role).filter(Role.id == id).options(subqueryload('*'))).first()

handler = GraphQL(
    make_executable_schema(load_schema_from_path('api/types/profiles.graphql'), query),
    debug = True
).http_handler

def serve(request: Request) -> Response:
    return handler.graphql_http_server(request)
