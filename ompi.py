# coding: utf-8


class OmpiInfoNode(object):
    def __init__(self):
        self._value = None
        self._dict = {}

    def _get_value(self):
        return self._value

    def _set_value(self, v):
        self._value = v

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, val):
        self._dict[key] = val

    def __contains__(self, key):
        return self._dict.__contains__(key)

    value = property(_get_value, _set_value)


def parse_ompi_info(out):
    root = OmpiInfoNode()
    lines = out.split("\n")

    for line in lines:
        items = line.split(':')
        val = items[-1]
        items = items[:-1]

        node = root
        for i in items:
            if i not in node:
                node[i] = OmpiInfoNode()
            node = node[i]
        node['value'] = val

    return root
