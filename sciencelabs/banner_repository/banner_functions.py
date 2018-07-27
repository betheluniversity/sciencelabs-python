from flask import abort
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from sciencelabs import app
from sciencelabs import banner_connection_is_working


constr = "oracle+cx_oracle://%s@(DESCRIPTION = (LOAD_BALANCE=on)\
    (FAILOVER=ON) (ADDRESS = (PROTOCOL = TCP)(HOST = banproddb.its.bethel.edu)(PORT = 1521))\
    (CONNECT_DATA = (SERVER = DEDICATED) (SERVICE_NAME = PROD8.its.bethel.edu)))"

bw = True
if bw:
    constr %= app.config['DB_KEY_BW']
else:
    constr %= app.config['DB_KEY']


engine_bw = create_engine(constr, convert_unicode=True)
db_session_bw = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine_bw))
conn_bw = engine_bw.raw_connection()


# a decorator to call db methods multiple times, if they fail
def try_db_method_twice(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return_value = False
        # try 2 times
        for i in [0, 1]:
            try:
                # if you get a non abort(503) value, return
                return_value = f(*args, **kwargs)
                break
            except:
                continue

        if return_value is not None:
            return return_value
        else:
            return abort(503)
    return decorated


def get_results(result, label="", type=None):
    ret = {}
    for i, row in enumerate(result):
        row_dict = {}
        for item in row:
            if isinstance(item, str) or isinstance(item, unicode):
                item = item.split(":", 1)
            else:
                # blob
                item = item.read()
            if len(item) > 1:
                row_dict[item[0]] = item[1]
            else:
                # if the result set doens't have key / value pairs
                # use a custom label
                row_dict[label] = item[0]

        ret[int(i)] = row_dict

    return ret


@try_db_method_twice
def portal_profile(username):
    try:
        call_cursor_bw = conn_bw.cursor()
        result_cursor_bw = conn_bw.cursor()
        call_cursor_bw.callproc('bth_portal_channel_api.bu_profile', (username, result_cursor_bw,))
        r = result_cursor_bw.fetchall()
        banner_connection_is_working['value'] = True
        return get_results(r)
    except:
        # if mybethel can't get the data, then prevent anything from loading
        banner_connection_is_working['value'] = False
        return abort(503)