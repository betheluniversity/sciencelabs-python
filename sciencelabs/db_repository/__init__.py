import urllib.parse
# Packages
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine
from functools import wraps

# Local
from sciencelabs import app

db = create_engine(app.config['DATABASE_KEY'], convert_unicode=True)
base = declarative_base()
db_session = sessionmaker(bind=db, autoflush=False)

# def try_db_method_twice(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         return_value = False
#         # try 2 times
#         for i in [0, 1]:
#             try:
#                 # if you get a non abort(503) value, return
#                 return_value = f(*args, **kwargs)
#                 break
#             except:
#                 continue
#
#         if return_value is not None:
#             return return_value
#         else:
#             return abort(503)
#
#     return decorated



