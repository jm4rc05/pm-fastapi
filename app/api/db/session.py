from decouple import config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


user = config('POSTGRES_USER')
password = config('POSTGRES_PASSWORD')
host = config('POSTGRES_HOST')
port = config('POSTGRES_PORT')
database = config('POSTGRES_DATABASE')

DATABASE_URL = f'postgresql+pg8000://{user}:{password}@{host}:{port}/{database}'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind = engine)
