import pathlib
from hashlib import blake2b
import os
import json


def define_path_json(path):
    global path_json
    path_json = pathlib.Path(str(pathlib.Path(path).parent.absolute()) + os.sep + 'DB_Signature.json')

 
def hash_blake2b(fname):
    if not os.path.isfile(fname):
        return "NO_DATA"
    hash_blake2b = blake2b(key=b'chiaveSegreta', digest_size=64)
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_blake2b.update(chunk)
    return hash_blake2b.hexdigest()


# assume the json has already been created
def check_db(fname):
    data = json.load(open(path_json))
    hash_old_value = data[fname]
    hash_new_value = hash_blake2b(fname)
    if hash_old_value == hash_new_value:
        return True
    else:
        return False
    

def add_db_to_json(path):
    # Check if the file exists, if it doesn't exist we create it
    if not os.path.isfile(path_json):
        new = {path: hash_blake2b(path)}
        with open(path_json, "w") as outfile:
            json.dump(new, outfile)
    data = json.load(open(path_json))
    new = {path: hash_blake2b(path)}
    data.update(new)
    with open(path_json, "w") as outfile:
        json.dump(data, outfile)


def check_db_exist(path):
    if not os.path.isfile(path_json):
        return False
    data = json.load(open(path_json))
    try:
         value = data[path]
    except KeyError:
        return False
    return True


def mod_dt_json(path):
    data = json.load(open(path_json))
    data[path] = hash_blake2b(path)
    with open(path_json, "w") as outfile:
        json.dump(data, outfile)
