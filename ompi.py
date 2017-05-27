# coding: utf-8

import re


class OmpiInfo(object):
    def __init__(self):
        self._dict = {}

    def get(self, prop):
        if prop not in self._dict:
            return None

        return self._dict[prop]

    def set(self, prop, value):
        self._dict[prop] = value


def _parse_single_val(val):
    if val in ['true', 'yes']:
        val = True
    if val in ['false', 'no']:
        val = False
    if val in ['none']:
        val = None

    return val


def parse_ompi_info(out):
    info = OmpiInfo()
    lines = out.split("\n")

    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue
        m = re.search(r'^(.*):([^:]+)?$', line)

        key, val = m.group(1), _parse_single_val(m.group(2))

        info.set(key, val)

    return info
