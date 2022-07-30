from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import URI

def postgres_db():
    e = create_engine(URI) 
    return sessionmaker(bind=e, autoflush=False)()