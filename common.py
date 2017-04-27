# coding: utf-8

import glob
import os.path
import re

def filter_path(proj_root, paths):
    links = glob.glob(os.path.join(proj_root, 'links', '*'))

    llp = []

    for p in paths:
        root = re.sub(r'/(bin|lib|lib64)/?$', '', p)
        if root not in links:
            llp.append(p)

    return llp
