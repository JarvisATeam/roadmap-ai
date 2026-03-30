from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from .models import Base

DB_PATH = Path.home() / '.roadmap' / 'roadmap.db'

def init_db():
    '''Initialize database and create tables'''
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f'sqlite:///{DB_PATH}')
    Base.metadata.create_all(engine)
    return engine

def get_session():
    '''Get database session'''
    engine = create_engine(f'sqlite:///{DB_PATH}')
    Session = sessionmaker(bind=engine)
    return Session()
