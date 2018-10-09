from flask import abort
from functools import wraps

from sciencelabs.oracle_procs.db_connection import conn_bw
from sciencelabs.views import banner_connection_is_working


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
            if isinstance(item, str):  # or isinstance(item, unicode):  TODO: Make sure this isn't needed
                item = item.split(":", 1)
            else:
                # blob
                item = item.read()
            if len(item) > 1:
                row_dict[item[0]] = item[1]
            else:
                # if the result set doesn't have key / value pairs use a custom label
                row_dict[label] = item[0]

        ret[int(i)] = row_dict

    return ret


# @try_db_method_twice
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


def get_username_from_name(fname, lname):
    call_cursor = conn_bw.cursor()
    result_cursor = conn_bw.cursor()
    fname = encode_percent(fname)
    lname = encode_percent(lname)

    call_cursor.callproc("bth_websrv_api.name_search", (fname, lname, result_cursor))
    result = result_cursor.fetchall()

    return get_results(result)


def encode_percent(str):
    return '%' + str + '%'


def get_course_is_valid(sbj, code):
    call_cursor = conn_bw.cursor()
    result_cursor = conn_bw.cursor()

    call_cursor.callproc("bth_websrv_api.course_num_is_valid", (sbj, code, result_cursor))
    result = result_cursor.fetchall()

    return get_results(result)


def get_info_for_course(sbj, code, date_offset=0):
    call_cursor = conn_bw.cursor()
    result_cursor = conn_bw.cursor()

    call_cursor.callproc("bth_websrv_api.coursecode_to_courses", (sbj, code, date_offset, result_cursor))
    result = result_cursor.fetchall()

    return get_results(result)


# @try_db_method_twice
def student_course_list(username, term_code=None):
    try:
        call_cursor_bw = conn_bw.cursor()
        result_cursor_bw = conn_bw.cursor()

        call_cursor_bw.callproc('bth_portal_channel_api.class_list_stu', (username, term_code, result_cursor_bw,))
        result = result_cursor_bw.fetchall()
        results = get_results(result)

        return results
    except:
        return abort(503)
