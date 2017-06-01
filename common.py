# coding: utf-8

import distutils.spawn
import glob
import os.path
import re
import shutil
from subprocess import call
from subprocess import check_output
from subprocess import PIPE
from subprocess import Popen
import sys

from ompi import parse_ompi_info
from py import PyLib

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


class BrokenSymlinkError(Exception):
    def __init__(self, message, path):
        super(BrokenSymlinkError).__init__(self, message)
        self.path = path


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


def which(cmd):
    exe = distutils.spawn.find_executable(cmd)
    if exe is None:
        return None

    exe = decode(os.path.realpath(exe))
    return exe


def filter_path(proj_root, paths):
    vers = glob.glob(os.path.join(proj_root, 'versions', '*'))

    llp = []

    for p in paths:
        root = re.sub(r'/(bin|lib|lib64)/?$', '', p)
        if root not in vers:
            llp.append(p)

    return llp


def is_active(prefix):
    mpiexec1 = os.path.realpath(os.path.join(prefix, 'bin', 'mpiexec'))
    mpiexec2 = which('mpiexec')
    return mpiexec1 == mpiexec2


def _get_info_mpich(prefix):
    info = {}

    # Run mpiexec --version and extract some information
    mpiexec = os.path.join(prefix, 'bin', 'mpiexec')
    out = decode(check_output([mpiexec, '--version']))

    # Parse 'Configure options' section
    # Config options are like this:
    # '--disable-option-checking' '--prefix=NONE' '--enable-cuda'
    m = re.search(r'Configure options:\s+(.*)$', out, re.MULTILINE)
    conf_str = m.group(1)
    conf_list = [s.replace("'", '') for s
                 in re.findall(r'\'[^\']+\'', conf_str)]

    m = re.search(r'Version:\s+(\S+)', out, re.MULTILINE)
    ver = m.group(1)

    if os.path.islink(prefix):
        path = os.path.realpath(prefix)
    else:
        path = prefix

    info['type'] = 'MPICH'
    info['active'] = is_active(prefix)
    info['version'] = ver
    info['path'] = path
    info['configure'] = conf_list[0]
    info['conf_params'] = conf_list
    info['default_name'] = "mpich-{}".format(ver)

    return info


def _get_info_mvapich(prefix):
    info = _get_info_mpich(prefix)

    # Parse mvapich version
    mpi_h = os.path.join(prefix, 'include', 'mpi.h')
    if not os.path.exists(mpi_h):
        raise RuntimeError("Error: Cannot find {}".format(mpi_h))

    mv_ver = check_output(['grep', '-E', 'define *MVAPICH2_VERSION', mpi_h],
                          stderr=DEVNULL)
    mch_ver = check_output(['grep', '-E', 'define *MPICH_VERSION', mpi_h],
                           stderr=DEVNULL)

    mv_ver = decode(mv_ver)
    mch_ver = decode(mch_ver)

    mv_ver = re.search(r'"([.0-9]+)"', mv_ver).group(1)
    mch_ver = re.search(r'"([.0-9]+)"', mch_ver).group(1)

    info['version'] = mv_ver
    info['type'] = 'MVAPICH'
    info['mpich_ver'] = mch_ver
    info['default_name'] = "mvapich2-{}".format(mv_ver)

    return info


def _call_ompi_info(bin):
    out = check_output([bin, '--all', '--parsable'], stderr=DEVNULL)
    out = decode(out)

    return parse_ompi_info(out)


def _get_info_ompi(prefix):
    info = {}

    ompi = _call_ompi_info(os.path.join(prefix, 'bin', 'ompi_info'))

    ver = ompi.get('ompi:version:full')
    mpi_ver = ompi.get('mpi-api:version:full')

    if os.path.islink(prefix):
        path = os.path.realpath(prefix)
    else:
        path = prefix

    info['type'] = 'Open MPI'
    info['active'] = is_active(prefix)
    info['version'] = ver
    info['mpi_version'] = mpi_ver
    info['prefix'] = prefix
    info['path'] = path
    info['configure'] = ""
    info['conf_params'] = []
    info['default_name'] = "openmpi-{}".format(ver)
    info['c'] = ompi.get('bindings:c')
    info['c++'] = ompi.get('bindings:cxx')
    info['fortran'] = ompi.get('bindings:mpif.h')

    return info


class Manager(object):
    def __init__(self, root_dir):
        self._root_dir = root_dir
        self._vers_dir = os.environ.get("MPIENV_VERSIONS_DIR",
                                        os.path.join(root_dir, 'versions'))
        self._load_info()

        if not os.path.exists(self._vers_dir):
            os.mkdir(self._vers_dir)

    def root_dir(self):
        return self._root_dir

    def _load_info(self):
        # Get the current status of the MPI environment.
        self._installed = {}
        for prefix in glob.glob(os.path.join(self._vers_dir, '*')):
            name = os.path.split(prefix)[-1]
            info = self.get_info(prefix)
            info['name'] = name
            self._installed[name] = info

    def get_info(self, name):
        """Obtain information of the MPI installed under prefix."""

        prefix = os.path.join(self._vers_dir, name)
        mpiexec = os.path.join(prefix, 'bin', 'mpiexec')
        mpi_h = os.path.join(prefix, 'include', 'mpi.h')

        if not os.path.exists(mpiexec):
            # This means the symlink under versions/ directory
            # is broken.
            # (The installed MPI has been removed after registration)
            return {
                'name': name,
                'broken': True,
            }

        p = Popen([mpiexec, '--version'], stderr=PIPE, stdout=PIPE)
        out, err = p.communicate()
        ver_str = decode(out + err)

        info = None

        if re.search(r'OpenRTE', ver_str, re.MULTILINE):
            info = _get_info_ompi(prefix)

        if re.search(r'HYDRA', ver_str, re.MULTILINE):
            # MPICH or MVAPICH
            # if mpi.h is installed, check it to identiy
            # the MPI type.
            # This is because MVAPCIH uses MPICH's mpiexec,
            # so we cannot distinguish them only from mpiexec.
            ret = call(['grep', 'MVAPICH2_VERSION', '-q', mpi_h],
                       stderr=DEVNULL)
            if ret == 0:
                # MVAPICH
                info = _get_info_mvapich(prefix)
            else:
                # MPICH
                # on some platform, sometimes only runtime
                # is installed and developemnt kit (i.e. compilers)
                # are not installed.
                # In this case, we assume it's mpich.
                info = _get_info_mpich(prefix)

        if info is None:
            sys.stderr.write("ver_str = {}\n".format(ver_str))
            raise RuntimeError("Unknown MPI type '{}'".format(mpiexec))

        for bin in ['mpiexec', 'mpicc', 'mpicxx']:
            info[bin] = os.path.realpath(os.path.join(prefix, 'bin', bin))

        return info

    def items(self):
        return self._installed.items()

    def keys(self):
        return self._installed.keys()

    def __getitem__(self, key):
        return self._installed[key]

    def __contains__(self, key):
        return key in self._installed

    def mpiexec(self, name):
        return os.path.realpath(os.path.join(
            self._vers_dir, name, 'bin', 'mpiexec'))

    def is_installed(self, path):
        # Find mpiexec in the path or something and check if it is already
        # under our control.
        assert type(path) == str or type(path) == bytes
        mpiexec = None
        path = os.path.realpath(path)
        if os.path.isdir(path):
            mpiexec = os.path.realpath(os.path.join(path, 'bin', 'mpiexec'))
        else:
            raise RuntimeError("todo: path={}".format(path))

        for name, info in self.items():
            if info['mpiexec'] == mpiexec:
                return name

        return None

    def get_current_name(self):
        return next(name for name, info in self.items() if info['active'])

    def add(self, prefix, name=None):
        n = self.is_installed(prefix)
        if n is not None:
            raise RuntimeError("{} is already managed "
                               "as '{}'".format(prefix, n))

        info = self.get_info(prefix)

        if name is not None:
            raise RuntimeError("Specifed name '{}' is "
                               "already taken".format(name))
        else:
            name = info['default_name']
            if name in self:
                raise RuntimeError("Recommended name for {} is {}, "
                                   "but the name is "
                                   "already used.".format(prefix, name))

        # dst -> src
        dst = os.path.join(self._vers_dir, name)
        src = prefix

        os.symlink(src, dst)

        return name

    def rm(self, name):
        if name not in self:
            raise RuntimeError("No such MPI: '{}'".format(name))

        info = self.get_info(name)

        if not info.get('broken') and info['active']:
            sys.stderr.write("You cannot remove active MPI: "
                             "'{}'\n".format(name))
            exit(-1)

        path = os.path.join(self._vers_dir, name)
        os.remove(path)

    def rename(self, name_from, name_to):
        if name_from not in self:
            raise RuntimeError("No such MPI: '{}'".format(name_from))

        if name_to in self:
            raise RuntimeError("Name '{}' already exists".format(name_to))

        path_from = os.path.join(self._vers_dir, name_from)
        path_to = os.path.join(self._vers_dir, name_to)

        shutil.move(path_from, path_to)

    def use(self, name):
        if name not in self:
            sys.stderr.write("mpienv-use: Error: "
                             "unknown MPI installation: "
                             "'{}'\n".format(name))
            exit(-1)

        info = self.get_info(name)

        if info.get('broken'):
            sys.stderr.write("mpienv-use: Error: "
                             "'{}' seems to be broken. Maybe it is removed.\n"
                             "".format(name))
            exit(-1)

        dst = os.path.join(self._root_dir, 'shims')

        # check if `name` is the currently active one,
        # and do nothing if so
        cur_mpi = os.path.realpath(os.path.join(self._root_dir, 'shims'))
        trg_mpi = os.path.realpath(os.path.join(self._vers_dir, name))

        if cur_mpi == trg_mpi:
            print("You are already using {}".format(name))
            return True

        if os.path.exists(dst):
            os.remove(dst)

        src = os.path.realpath(os.path.join(self._vers_dir, name))

        os.symlink(src, dst)

        pylib = PyLib()


_root_dir = (os.environ.get("MPIENV_ROOT", None) or
             os.path.join(os.path.expanduser('~'), '.mpienv'))
manager = Manager(_root_dir)
