from contextlib import contextmanager
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from decouple import config

postgres_user = config('POSTGRES_USER')
postgres_password = config('POSTGRES_PASSWORD')
postgres_host = config('POSTGRES_HOST')
postgres_port = config('POSTGRES_PORT')
postgres_database = config('POSTGRES_DATABASE')

DATABASE_URL = f'postgresql+pg8000://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_database}'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()

@staticmethod
@contextmanager
def session_factory():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
