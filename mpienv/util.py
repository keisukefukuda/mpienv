# coding: utf-8
import glob
import os.path


def glob_list(dire, pat_list):
    """Glob all patterns `pat` in `directory`"""
    if type(dire) is list or type(dire) is tuple:
        dire = os.path.join(*dire)

    # list of lists
    lol = [glob.glob(os.path.join(dire, p)) for p in pat_list]

    # return flattened list
    return [item for sublist in lol for item in sublist]
