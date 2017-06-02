# coding: utf-8

from __future__ import print_function
import errno
import glob
import os
import os.path
import platform
import re
import shutil
from subprocess import check_call
from subprocess import check_output
import sys


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class PyModule(object):
    def __init__(self, libname, root_dir, name):
        pybin = os.path.realpath(sys.executable)
        pybin_enc = re.sub(r'[^a-zA-Z0-9.]', '_', re.sub('^/', '', pybin))

        self._libname = libname
        self._root_dir = os.path.abspath(root_dir)
        self._pylib_dir = os.path.abspath(os.path.join(self._root_dir,
                                                       'pylib',
                                                       pybin_enc,
                                                       name))
        self._name = name

        if not os.path.exists(self._pylib_dir):
            mkdir_p(self._pylib_dir)

    def is_installed(self):
        libs = glob.glob(os.path.join(self._pylib_dir, self._libname, '*.so'))
        return len(libs) > 0

    def install(self):
        PATH = os.path.join(self._root_dir, 'versions', self._name, 'bin')
        LD =os.path.join(self._root_dir, 'versions', self._name, 'lib')
        
        env = os.environ.copy()
        env['PATH'] = "{}:{}".format(PATH, env['PATH'])
        env['LD_LIBRARY_PATH'] = "{}:{}".format(LD, env['LD_LIBRARY_PATH'])

        sys.stderr.write("Installing {} for {} ...\n".format(self._libname,
                                                             self._name))
        check_call(['pip', 'install', '-t', self._pylib_dir,
                    '--no-cache-dir', self._libname],
                   stdout=sys.stderr, env=env)

    def use(self):
        pypath = os.environ.get('PYTHONPATH', None)
        if pypath is None:
            pypath = [self._pylib_dir]
        else:
            paths = [p for p in pypath.split(':') if p.find(self._root_dir) < 0]
            paths[:0] = [self._pylib_dir]
            pypath = ':'.join(paths)

        print("export PYTHONPATH={}".format(pypath))


class MPI4Py(PyModule):
    def __init__(self, root_dir, name):
        super(MPI4Py, self).__init__('mpi4py', root_dir, name)

