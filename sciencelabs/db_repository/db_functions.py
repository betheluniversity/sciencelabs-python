from sciencelabs.db_repository.db_connection_bw import conn_bw


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

def user(username):
    call_cursor_bw = conn_bw.cursor()
    result_cursor_bw = conn_bw.cursor()
    call_cursor_bw.callproc('bth_portal_channel_api.bu_profile', (username, result_cursor_bw,))
    r = result_cursor_bw.fetchall()
    return get_results(r)
