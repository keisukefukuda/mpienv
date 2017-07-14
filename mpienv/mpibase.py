# coding: utf-8

import os.path


class MpiBase(object):
    def __init__(self, prefix, conf):
        self._prefix = prefix
        self._conf = conf

    @property
    def mpiexec(self):
        ex = os.path.join(self._prefix, 'bin', 'mpiexec')
        if os.path.islink(ex):
            ex2 = os.readlink(ex)
            if not os.path.isabs(ex2):
                ex2 = os.path.join(os.path.dirname(ex), ex2)
            
        return ex2
