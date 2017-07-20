# coding: utf-8
import glob
import json
import os.path
import sys

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


def glob_list(dire, pat_list):
    """Glob all patterns `pat` in `directory`"""
    if type(dire) is list or type(dire) is tuple:
        dire = os.path.join(*dire)

    # list of lists
    lol = [glob.glob(os.path.join(dire, p)) for p in pat_list]

    # return flattened list
    return [item for sublist in lol for item in sublist]


def decode(s):
    if type(s) == bytes:
        return s.decode(sys.getdefaultencoding())
    else:
        return s


def encode(s):
    if type(s) == str:
        return s.encode(sys.getdefaultencoding())
    else:
        return s


def dump_json(obj):
    try:
        return json.dumps(obj)
    except TypeError:
        return obj.to_dict()
