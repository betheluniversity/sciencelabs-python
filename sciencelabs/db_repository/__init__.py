import urllib.parse

# Packages
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

# Local
from sciencelabs import app

db = create_engine(app.config['DATABASE_KEY'], convert_unicode=True)
base = declarative_base()
session_maker = sessionmaker(bind=db)
db_session = session_maker()



