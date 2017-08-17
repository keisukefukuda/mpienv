# coding: utf-8

from __future__ import print_function
import errno
import glob
import os
import os.path
import shutil
from subprocess import check_call
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
    def __init__(self, libname, conf, name):
        self._libname = libname
        self._root_dir = conf['root_dir']
        self._mpi_dir = conf['mpi_dir']
        self._pylib_dir = os.path.join(conf['pylib_dir'], name)
        self._name = name
        self._conf = conf

        if not os.path.exists(self._pylib_dir):
            mkdir_p(self._pylib_dir)

    def is_installed(self):
        libs = glob.glob(os.path.join(self._pylib_dir, self._libname, '*.so'))
        return len(libs) > 0

    def install(self):
        PATH = os.path.join(self._mpi_dir, 'bin')
        LD = os.path.join(self._mpi_dir, 'lib')

        env = os.environ.copy()
        env['PATH'] = "{}:{}".format(PATH, env['PATH'])

        if env.get('LD_LIBRARY_PATH'):
            env['LD_LIBRARY_PATH'] = "{}:{}".format(LD,
                                                    env.get('LD_LIBRARY_PATH'))
        else:
            env['LD_LIBRARY_PATH'] = "{}".format(LD)

        with open(os.devnull, 'w') as devnull:
            sys.stderr.write(
                "Installing {} using pip...".format(self._libname))
            sys.stderr.flush()
            check_call(['pip', 'install', '-v',
                        '-t', self._pylib_dir,
                        # '--no-cache-dir',
                        self._libname],
                       stdout=sys.stderr,
                       # stdout=devnull,
                       env=env)
            devnull  # NOQA
            sys.stderr.write(" done.\n")
            sys.stderr.flush()

    def use(self):
        pypath = os.environ.get('PYTHONPATH', None)
        if pypath is None:
            paths = [self._pylib_dir]
        else:
            # Split path and remove directories managed by mpienv
            paths = [p for p in pypath.split(':')
                     if p.find(self._root_dir) < 0]
            paths[:0] = [self._pylib_dir]
        pypath = ':'.join(paths)

        print("export PYTHONPATH={}".format(pypath))

    def clear(self):
        pypath = os.environ.get('PYTHONAPTH', "")
        newpath = ':'.join([p for p in pypath.split(':')
                            if not p.startswith(self._conf['pylib_dir'])])

        if newpath == "":
            print("unset PYTHONPATH")
        else:
            print("export PYTHONPATH={}".format(newpath))

    def rm(self):
        if os.path.exists(self._pylib_dir):
            shutil.rmtree(self._pylib_dir)

    def rename(self, name_to):
        """Rename the directory, where the module is installed, to `name_to`

        This function is used together with `Mpienv.rename()`.
        """
        path_from = self._pylib_dir
        path_to = os.path.join(self._conf['pylib_dir'], name_to)

        shutil.move(path_from, path_to)
        self._name = name_to
        self._pylib_dir = path_to


class MPI4Py(PyModule):
    def __init__(self, conf, name):
        super(MPI4Py, self).__init__('mpi4py', conf, name)
