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
from api.db.models.orders import Product, Cart, Item


load_dotenv('.env.local')

logging.config.fileConfig(f'{ROOT_DIR}/logging.conf')
logger = logging.getLogger()

API_MAXIMUM_COST = config('API_MAXIMUM_COST', cast = int, default = 5)
logger.info(f'API maximum cost: {API_MAXIMUM_COST}')

query = QueryType()
mutation = MutationType()


def serve(request: Request) -> Response:
    load_path = 'api/types/orders.graphql'
    defs = load_schema_from_path(load_path)
    schema = make_executable_schema(defs, [query, mutation])
    return GraphQL(
        schema, 
        logger = logging.Logger, 
        validation_rules = [ cost_validator(maximum_cost = API_MAXIMUM_COST) ],
        debug = True
    ).http_handler.graphql_http_server(request)
