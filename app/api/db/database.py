import os, logging
from contextlib import contextmanager
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from decouple import config
from dotenv import load_dotenv
from constants import ROOT_DIR


load_dotenv('.env.local')

POSTGRES_USER = config('POSTGRES_USER')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')
POSTGRES_HOST = config('POSTGRES_HOST')
POSTGRES_PORT = config('POSTGRES_PORT')
POSTGRES_DATABASE = config('POSTGRES_DATABASE')

DATABASE_URL = f'postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()

@staticmethod
@contextmanager
def session_factory() -> Session:
    db = SessionLocal()
    try:
        logging.info(f'Session to postgres at {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE} created')
        yield db
    finally:
        logging.info(f'Session to postgres at {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE} closed')
        db.close()
