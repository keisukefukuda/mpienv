# coding: utf-8

from configparser import ConfigParser
import json
import os.path
import re
import sys

from mpienv.mpi import BrokenMPI
from mpienv.mpi import get_mpi_class
from mpienv.py import MPI4Py

try:
    exec("import __builtin__")  # To avoid IDE's grammar check
except ImportError:
    import builtins


class UnknownMPI(RuntimeError):
    pass


try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def yes_no_input(msg):
    try:
        input = eval("__builtin__.raw_input")
    except NameError:
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
        self._vers_dir = os.path.join(os.path.join(root_dir, 'versions'))
        pybin = os.path.realpath(sys.executable)
        pybin_enc = re.sub(r'[^a-zA-Z0-9.]', '_', re.sub('^/', '', pybin))

        self._mpi_dir = os.path.join(self._vers_dir, 'mpi')
        self._pylib_dir = os.path.join(self._vers_dir, 'pylib', pybin_enc)
        self._pybuild_dir = os.path.join(self._vers_dir, 'pybuild', pybin_enc)
        self._cache_dir = os.path.join(root_dir, 'cache')
        self._build_dir = os.path.join(root_dir, 'builds')

        self._make_directories()
        self._setup_config()

        self._load_mpi_info()

        self._conf['root_dir'] = self._root_dir
        self._conf['vers_dir'] = self._vers_dir
        self._conf['mpi_dir'] = self._mpi_dir
        self._conf['pylib_dir'] = self._pylib_dir
        self._conf['pybuild_dir'] = self._pybuild_dir
        self._conf['cache_dir'] = self._cache_dir
        self._conf['build_dir'] = self._build_dir

    def _make_directories(self):
        mkdir_p(self._root_dir)
        mkdir_p(self._vers_dir)
        mkdir_p(self._mpi_dir)
        mkdir_p(self._pylib_dir)
        mkdir_p(self._pybuild_dir)
        mkdir_p(self._cache_dir)
        mkdir_p(self._build_dir)

    def _setup_config(self):
        self.config2 = ConfigParser()

        if os.path.exists(self.config_file_path()):
            self.config2.read(self.config_file_path())

        self._load_config()

    def root_dir(self):
        return self._root_dir

    def config_file_path(self):
        return os.path.join(self._root_dir, 'mpienv.ini')

    def config_save(self):
        with open(self.config_file_path(), 'w') as f:
            self.config2.write(f)

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

        for name in self.config2:
            if name != 'DEFAULT':
                mpiexec = self.config2[name]['mpiexec']
                mpi = self.get_mpi_from_mpiexec(mpiexec)
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
            mpi_class = get_mpi_class(self, mpiexec)
        except FileNotFoundError:
            return BrokenMPI(mpiexec, self._conf)

        return mpi_class(mpiexec, self._conf)

    def prefix(self, name):
        return os.path.join(self._mpi_dir, name)

    def get_mpi_from_name(self, name):
        if name not in self.config2:
            sys.stderr.write("mpienv: Error: "
                             "unknown MPI installation: "
                             "'{}'\n".format(name))
            exit(-1)

        mpiexec = self.config2[name]['mpiexec']
        mpi_class = get_mpi_class(self, mpiexec)
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

        for name in self.config2:
            if name != 'DEFAULT':
                if self.config2[name]['mpiexec'] == mpiexec:
                    return name

        return None

    def get_current_name(self):
        if 'DEFAULT' in self.config2 and 'active' in self.config2['DEFAULT']:
            name = self.config2['DEFAULT']['active']

            # Check
            if not self.get_mpi_from_name(name).is_active:
                sys.stderr.write("mpienv: Error: Internal status is "
                                 "inconsistent. Please hit 'mpienv use' "
                                 "command to refresh the status.\n")
                exit(1)
            return name
        else:
            raise RuntimeError("No MPI is activated.")

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
            sys.stderr.write("'{}' is already managed "
                             "as '{}'\n".format(target, n))
            exit(1)

        if self._installed.get(name) is not None:
            sys.stderr.write("Specifed name '{}' is "
                             "already taken\n".format(name))
        elif name is None:
            name = mpi.default_name
            if name in self:
                sys.stderr.write("Error: "
                                 "Recommended name for {} is {}, "
                                 "but the name is "
                                 "already used. "
                                 "Try -n option.\n".format(target, name))
                exit(-1)

        if name in self.config2:
            sys.stderr.write("{} is already registered.\n".format(name))
        else:
            self.config2.add_section(name)
            self.config2[name]['name'] = name
            self.config2[name]['mpiexec'] = target
            self.config_save()

        return name

    def rm(self, name, prompt=False):
        mpi = self.get_mpi_from_name(name)

        if not mpi.is_broken and mpi.is_active:
            sys.stderr.write("You cannot remove active MPI: "
                             "'{}'\n".format(name))
            exit(-1)

        if (not prompt) or yes_no_input("Remove '{}' ?".format(name)):
            self.config2.remove_section(name)
            self.config_save()

        mpi4py = MPI4Py(self._conf, name)
        if mpi4py.is_installed():
            mpi4py.rm()

    def rename(self, name_from, name_to):
        if name_from not in self.config2:
            raise RuntimeError("No such MPI: '{}'".format(name_from))

        if name_to in self.config2:
            raise RuntimeError("Name '{}' already exists".format(name_to))

        v = self.config2[name_from]
        self.config2[name_to] = v
        self.config2.remove_section(name_from)
        self.config_save()

        mpi4py = MPI4Py(self._conf, name_from)
        if mpi4py.is_installed():
            mpi4py.rename(name_to)

    def use(self, name, no_mpi4py=False):
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

        mpi.use(name, no_mpi4py=no_mpi4py)

    def exec_(self, cmds, **kwargs):
        try:
            name = self.get_current_name()
        except RuntimeError:
            sys.stderr.write("mpienv: Error: No MPI is currently activated.\n")
        mpi = self.get_mpi_from_name(name)
        mpi.exec_(cmds, **kwargs)

    def restore(self):
        if 'DEFAULT' in self.config2:
            try:
                mpi_name = self.config2['DEFAULT']['active']
                if 'mpi4py' in self.config2['DEFAULT']:
                    mpi4py = self.config2['DEFAULT'].getboolean('mpi4py')
                else:
                    mpi4py = True
            except KeyError:
                return
            self.use(mpi_name, mpi4py)

    def describe(self, name):
        mpi = self.get_mpi_from_name(name)
        mpi.describe()


_root_dir = (os.environ.get("MPIENV_ROOT", None) or
             os.path.join(os.path.expanduser('~'), '.mpienv'))
mpienv = Mpienv(_root_dir)
