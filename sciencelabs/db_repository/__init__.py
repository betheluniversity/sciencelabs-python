import urllib.parse

# Packages
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

# Local
from sciencelabs import app, db

database = db.create_engine(app.config['DATABASE_KEY'], convert_unicode=True)
Base = declarative_base()
Session = sessionmaker(bind=database)
session = Session()



