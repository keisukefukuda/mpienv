# coding: utf-8

import glob
import json
import os.path
import re
import shutil
import sys

from mpienv.mpi import BrokenMPI
from mpienv.mpi import MPI
from mpienv.py import MPI4Py

try:
    import __builtin__
except ImportError:
    import builtins


class UnknownMPI(RuntimeError):
    pass


try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def yes_no_input(msg):
    if hasattr(__builtin__, 'raw_input'):
        input = __builtin__.raw_input
    else:
        input = builtins.input

    try:
        choice = input("{} [y/N]: ".format(msg)).lower()
        while True:
            if choice in ['y', 'ye', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            else:
                choice = input(
                    "Please respond with 'yes' or 'no' [y/N]: ").lower()
    except (EOFError, KeyboardInterrupt):
        return False


def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)


DefaultConf = {
    'mpich': {
    },
    'mvapich': {
    },
    'openmpi': {
    },
}


class Mpienv(object):
    def __init__(self, root_dir):
        self._root_dir = root_dir
        self._vers_dir = os.path.join(os.environ.get("MPIENV_VERSIONS_DIR") or
                                      os.path.join(root_dir, 'versions'))
        self._shims_dir = os.path.join(self._vers_dir, 'shims')
        pybin = os.path.realpath(sys.executable)
        pybin_enc = re.sub(r'[^a-zA-Z0-9.]', '_', re.sub('^/', '', pybin))

        self._mpi_dir = os.path.join(self._vers_dir, 'mpi')
        self._pylib_dir = os.path.join(self._vers_dir, 'pylib', pybin_enc)
        self._pybuild_dir = os.path.join(self._vers_dir, 'pybuild', pybin_enc)
        self._cache_dir = os.environ.get("MPIENV_CACHE_DIR",
                                         os.path.join(root_dir, 'cache'))
        self._build_dir = os.environ.get("MPIENV_BUILD_DIR",
                                         os.path.join(root_dir, 'builds'))

        mkdir_p(self._vers_dir)
        mkdir_p(self._mpi_dir)
        mkdir_p(self._pylib_dir)
        mkdir_p(self._pybuild_dir)
        mkdir_p(self._cache_dir)
        mkdir_p(self._build_dir)

        self._load_config()
        self._load_mpi_info()

        self._conf['root_dir'] = self._root_dir
        self._conf['vers_dir'] = self._vers_dir
        self._conf['mpi_dir'] = self._mpi_dir
        self._conf['pylib_dir'] = self._pylib_dir
        self._conf['pybuild_dir'] = self._pybuild_dir
        self._conf['cache_dir'] = self._cache_dir
        self._conf['build_dir'] = self._build_dir
        self._conf['shims_dir'] = self._shims_dir

    def root_dir(self):
        return self._root_dir

    def build_dir(self):
        return self._build_dir

    def cache_dir(self):
        return self._cache_dir

    def mpi_dir(self):
        return self._mpi_dir

    def pylib_dir(self):
        return self._pylib_dir

    def pybuild_dir(self):
        return self._pybuild_dir

    def _load_mpi_info(self):
        # Get the current status of the MPI environment.
        self._installed = {}
        for mpiexec_link in glob.glob(os.path.join(self._mpi_dir, '*')):
            assert(os.path.islink(mpiexec_link))
            name = os.path.split(mpiexec_link)[-1]
            try:
                mpiexec = os.readlink(mpiexec_link)
            except EnvironmentError:
                raise RuntimeError("Internal Error: {} is not a file or link"
                                   .format(mpiexec_link))
            try:
                mpi = self.get_mpi_from_mpiexec(mpiexec)
            except RuntimeError:
                # If the directory exists but MPI is not found,
                # then it's a broken MPI.
                if os.path.exists(mpiexec):
                    mpi = BrokenMPI(mpiexec)
                else:
                    sys.stderr.write("mpienv: [Warning] Directory '{}' "
                                     "is registered as {} but no mpiexec "
                                     "is found.\n".format(
                                         mpiexec,
                                         name))
                    continue  # skip
            mpi.name = name
            self._installed[name] = mpi

    def _load_config(self):
        conf_json = os.path.join(self._root_dir, "config.json")
        if os.path.exists(conf_json):
            with open(conf_json) as f:
                pass  # sys.stderr.write(f.read())
            with open(conf_json) as f:
                conf = json.load(f)
        else:
            # sys.stderr.write("Warning: Cannot find config file\n")
            conf = {}

        self._conf = DefaultConf.copy()
        self._conf.update(conf)

    def config(self):
        return self._conf

    def get_mpi_from_mpiexec(self, mpiexec):
        try:
            mpi_class = MPI(self, mpiexec)
        except FileNotFoundError:
            return BrokenMPI(mpiexec, self._conf)

        return mpi_class(mpiexec, self._conf)

    def prefix(self, name):
        return os.path.join(self._mpi_dir, name)

    def get_mpi_from_name(self, name):
        if name not in self:
            sys.stderr.write("mpienv: Error: "
                             "unknown MPI installation: "
                             "'{}'\n".format(name))
            exit(-1)

        mpiexec = os.readlink(os.path.join(self._mpi_dir, name))
        mpi_class = MPI(self, mpiexec)
        return mpi_class(mpiexec, self._conf, name)

    def items(self):
        return self._installed.items()

    def keys(self):
        return self._installed.keys()

    def __getitem__(self, key):
        try:
            return next(mpi for name, mpi in self._installed.items()
                        if name == key)
        except StopIteration:
            raise KeyError()

    def __contains__(self, key):
        return key in self._installed

    def mpiexec(self, name):
        return os.path.realpath(os.path.join(
            self._mpi_dir, name, 'bin', 'mpiexec'))

    def is_installed(self, mpiexec):
        # Find mpiexec in the path or something and check if it is already
        # under our control.
        prefix = os.path.abspath(os.path.join(os.path.dirname(mpiexec),
                                              os.path.pardir))
        assert os.path.isdir(prefix)

        for name, mpi in self.items():
            if os.path.realpath(mpi.mpiexec) == mpiexec:
                return name

        return None

    def get_current_name(self):
        try:
            return next(name for name, mpi in self.items() if mpi.is_active)
        except StopIteration:
            raise UnknownMPI()

    def add(self, target, name=None):
        # `target` is expected to be an mpiexec command or its prefix
        if os.path.isdir(target):
            # target seems to be prefix
            target = os.path.join(target, 'bin', 'mpiexec')

        mpi = self.get_mpi_from_mpiexec(target)

        if isinstance(mpi, BrokenMPI):
            sys.stderr.write("Cannot find MPI from {}. "
                             "The MPI installation "
                             "seems to be broken.\n".format(target))
            exit(-1)

        n = self.is_installed(target)
        if n is not None:
            raise RuntimeError("{} is already managed "
                               "as '{}'".format(target, n))

        if self._installed.get(name) is not None:
            raise RuntimeError("Specifed name '{}' is "
                               "already taken".format(name))
        elif name is None:
            name = mpi.default_name
            if name in self:
                sys.stderr.write("Error: "
                                 "Recommended name for {} is {}, "
                                 "but the name is "
                                 "already used. "
                                 "Try -n option.\n".format(target, name))
                exit(-1)

        # dst -> src
        dst = os.path.join(self._mpi_dir, name)
        src = target

        os.symlink(src, dst)

        return name

    def rm(self, name, prompt=False):
        mpi = self.get_mpi_from_name(name)

        if not mpi.is_broken and mpi.is_active:
            sys.stderr.write("You cannot remove active MPI: "
                             "'{}'\n".format(name))
            exit(-1)

        if (not prompt) or yes_no_input("Remove '{}' ?".format(name)):
            mpi.remove()

        mpi4py = MPI4Py(self._conf, name)
        if mpi4py.is_installed():
            mpi4py.rm()

    def rename(self, name_from, name_to):
        if name_from not in self:
            raise RuntimeError("No such MPI: '{}'".format(name_from))

        if name_to in self:
            raise RuntimeError("Name '{}' already exists".format(name_to))

        path_from = os.path.join(self._mpi_dir, name_from)
        path_to = os.path.join(self._mpi_dir, name_to)

        shutil.move(path_from, path_to)

        mpi4py = MPI4Py(self._conf, name_from)
        if mpi4py.is_installed():
            mpi4py.rename(name_to)

    def use(self, name, mpi4py=False):
        mpi = self.get_mpi_from_name(name)

        if isinstance(mpi, BrokenMPI):
            print(mpi)
            sys.stderr.write("mpienv-use: Error: "
                             "'{}' seems to be broken. Maybe it is removed.\n"
                             "".format(name))
            exit(-1)

        if mpi.is_broken:
            sys.stderr.write("mpienv-use: Error: "
                             "'{}' seems to be broken. Maybe it is removed.\n"
                             "".format(name))
            exit(-1)

        mpi.use(name, mpi4py=mpi4py)

    def exec_(self, cmds):
        name = self.get_current_name()
        mpi = self.get_mpi_from_name(name)
        mpi.exec_(cmds)


_root_dir = (os.environ.get("MPIENV_ROOT", None) or
             os.path.join(os.path.expanduser('~'), '.mpienv'))
mpienv = Mpienv(_root_dir)
