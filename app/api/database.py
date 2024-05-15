from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from decouple import config

user = config('POSTGRES_USER')
password = config('POSTGRES_PASSWORD')
host = config('POSTGRES_HOST')
port = config('POSTGRES_PORT')
database = config('POSTGRES_DATABASE')

DATABASE_URL = f'postgresql+pg8000://{user}:{password}@{host}:{port}/{database}'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()

def session_factory() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
