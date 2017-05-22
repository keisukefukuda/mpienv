# coding: utf-8

import distutils.spawn
import glob
import os.path
import re
from subprocess import call
from subprocess import check_output
import sys


def which(cmd):
    return os.path.realpath(distutils.spawn.find_executable(cmd))


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
    out = check_output([mpiexec, '--version'],
                       encoding=sys.getdefaultencoding())

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

    for bin in ['mpiexec', 'mpicc', 'mpicxx']:
        info[bin] = os.path.realpath(os.path.join(prefix, 'bin', bin))

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
                          encoding=sys.getdefaultencoding())
    mch_ver = check_output(['grep', '-E', 'define *MPICH_VERSION', mpi_h],
                           encoding=sys.getdefaultencoding())

    mv_ver = re.search(r'"([.0-9]+)"', mv_ver).group(1)
    mch_ver = re.search(r'"([.0-9]+)"', mch_ver).group(1)

    info['version'] = mv_ver
    info['type'] = 'MVAPICH'
    info['mpich_ver'] = mch_ver
    info['default_name'] = "mvapich-{}".format(mv_ver)

    return info


def _get_info_ompi(prefix):
    info = {}

    # Get the Open MPI version
    mpi_h = os.path.join(prefix, 'include', 'mpi.h')

    major_s = check_output(['grep', '-E', 'define OMPI_MAJOR_VERSION', mpi_h],
                           encoding=sys.getdefaultencoding())
    minor_s = check_output(['grep', '-E', 'define OMPI_MINOR_VERSION', mpi_h],
                           encoding=sys.getdefaultencoding())
    rel_s = check_output(['grep', '-E', 'define OMPI_RELEASE_VERSION', mpi_h],
                         encoding=sys.getdefaultencoding())

    major = re.search(r'\d+', major_s).group(0)
    minor = re.search(r'\d+', minor_s).group(0)
    rel = re.search(r'\d+', rel_s).group(0)

    ver = "{}.{}.{}".format(major, minor, rel)

    if os.path.islink(prefix):
        path = os.path.realpath(prefix)
    else:
        path = prefix

    for bin in ['mpiexec', 'mpicc', 'mpicxx']:
        info[bin] = os.path.realpath(os.path.join(prefix, 'bin', bin))

    info['type'] = 'Open MPI'
    info['active'] = is_active(prefix)
    info['version'] = ver
    info['prefix'] = prefix
    info['path'] = path
    info['configure'] = ""
    info['conf_params'] = []
    info['default_name'] = "ompi-{}".format(ver)

    return info


class Manager(object):
    def __init__(self, root_dir):
        self._root_dir = root_dir
        self._vers_dir = os.path.join(root_dir, 'versions')
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
            sys.stderr.write("Error: {} was not found. "
                             "MPI is not intsalled in this "
                             "path or only runtime".format(mpiexec))

        enc = sys.getdefaultencoding()
        ver_str = check_output([mpiexec, '--version']).decode(enc)

        if re.search(r'OpenRTE', ver_str, re.MULTILINE):
            return _get_info_ompi(prefix)

        if re.search(r'HYDRA', ver_str, re.MULTILINE):
            # MPICH or MVAPICH
            # if mpi.h is installed, check it to identiy
            # the MPI type.
            # This is because MVAPCIH uses MPICH's mpiexec,
            # so we cannot distinguish them only from mpiexec.
            if os.path.exists(mpi_h):
                ret = call(['grep', 'MVAPICH2_VERSION', '-q', mpi_h])
                if ret == 0:
                    # MVAPICH
                    return _get_info_mvapich(prefix)
                else:
                    # MPICH
                    return _get_info_mpich(prefix)
            else:
                # on some platform, sometimes only runtime
                # is installed and developemnt kit (i.e. compilers)
                # are not installed.
                # In this case, we assume it's mpich.
                return _get_info_mpich(prefix)

        raise RuntimeError("Unknown MPI type '{}'".format(mpiexec))

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

    def use(self, name):
        if name not in self:
            sys.stderr.write("mpienv-use: Error: "
                             "unknown MPI installation: "
                             "'{}'\n".format(name))
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


manager = Manager(os.path.join(os.path.expanduser('~'), '.mpienv'))
