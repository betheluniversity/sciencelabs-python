# Packages
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

# Local
from app_settings import app_settings


db = create_engine(app_settings['DATABASE_KEY'])
Base = declarative_base()
Session = sessionmaker(bind=db)
session = Session()



