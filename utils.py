import os
import json
from Cryptodome.Util.Padding import pad, unpad

FILE_BLOCK_SIZE = 2
TAGS_FILENAME = 'tags.json'
PUBLIC_DIR = 'all'
if not os.path.exists(PUBLIC_DIR):
    os.mkdir(PUBLIC_DIR)
PUBLIC_KEY_FILENAME = 'public_key.json'
PRIVATE_KEY_FILENAME = 'private_key.json'

def bytes_to_int(bdata : bytes):
    return int.from_bytes(bdata, 'little')

def int_to_bytes(idata : int):
    return idata.to_bytes(FILE_BLOCK_SIZE, 'little')

def concat_int_blocks(*args : int) -> int:
    '''
    for example: 
    ```python
    concat_int_blocks(0x01, 0x02, 0x03) -> 0x000300020001
    ```
    '''
    res = 0
    for idata in reversed(args):
        res = (res << FILE_BLOCK_SIZE*8) + idata
    return res

def release_tags(tags):
    with open(os.path.join(PUBLIC_DIR, TAGS_FILENAME), 'w') as f:
        json.dump(tags, f, indent=4)

def load_tags():
    with open(os.path.join(PUBLIC_DIR, TAGS_FILENAME), 'r') as f:
        return json.load(f)


def load_private_key(dirname):
    '''returns: p, q'''
    with open(os.path.join(dirname, PRIVATE_KEY_FILENAME), 'r') as f:
        skey = json.load(f)
    return skey['p'], skey['q']

def load_public_key(dirname = PUBLIC_DIR):
    '''returns: N, g'''
    with open(os.path.join(dirname, PUBLIC_KEY_FILENAME), 'r') as f:
        pkey = json.load(f)
    return pkey['N'], pkey['g']

def release_public_key(src_dirname):
    '''publish: N, g'''
    with open(os.path.join(src_dirname, PUBLIC_KEY_FILENAME), 'r') as f:
        pkey = json.load(f)

    with open(os.path.join(PUBLIC_DIR, PUBLIC_KEY_FILENAME), 'w') as f:
        json.dump(pkey, f, indent=4)

def read_pad_data(filename):
    with open(filename, 'rb') as f:
        data = pad(f.read(), FILE_BLOCK_SIZE)
    return data


def write_unpad_data(filename, data):
    with open(filename, 'wb') as f:
        f.write(unpad(data, FILE_BLOCK_SIZE))

def split_message(data):
    m = [data[i : i + FILE_BLOCK_SIZE] for i in range(0, len(data), FILE_BLOCK_SIZE)]
    m = [bytes_to_int(mi) for mi in m]
    return m