from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine
from functools import wraps

# Local
from sciencelabs import app

db = create_engine(app.config['DATABASE_KEY'], convert_unicode=True)
base = declarative_base()
session_maker = sessionmaker(bind=db, autoflush=False)
db_session = session_maker()


# This allows me to decorate all functions in a class
def decorate_all_functions(function_decorator):
    def decorator(cls):
        for name, obj in vars(cls).items():
            if callable(obj):
                try:
                    obj = obj.__func__  # unwrap Python 2 unbound method
                except AttributeError:
                    pass  # not needed in Python 3
                setattr(cls, name, function_decorator(obj))
        return cls
    return decorator


# This decorator closes the db session after every call to ensure the data propagates.
def close_db_session(func):
    @wraps(func)
    def wrapper(*args, **kw):
        try:
            res = func(*args, **kw)
        finally:
            db_session.close()
        return res

    return wrapper


