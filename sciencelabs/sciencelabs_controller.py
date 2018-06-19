# Global
import os


def get_app_settings():
    to_return = {}
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
    final_path = os.path.join(parent_dir_path, 'app_settings.py')
    with open(final_path) as f:
        for line in f.readlines():
            key, val = line.split(' = ')
            to_return[key] = val[1:-2]  # This peels off a ' from the front and a '\n from the end
    return to_return
