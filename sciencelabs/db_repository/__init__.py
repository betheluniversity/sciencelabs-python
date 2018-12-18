import urllib.parse

# Packages
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

# Local
from sciencelabs import app

db = create_engine(app.config['DATABASE_KEY'].format(urllib.parse.quote_plus(app.config['DATABASE_PASS'])))
Base = declarative_base()
Session = sessionmaker(bind=db)
session = Session()



