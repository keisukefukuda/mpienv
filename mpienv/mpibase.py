# coding: utf-8

import distutils.spawn
import os.path
import shutil
from subprocess import Popen
import sys  # NOQA

from mpienv.py import MPI4Py
import mpienv.util


def _which(cmd):
    exe = distutils.spawn.find_executable(cmd)
    if exe is None:
        return None

    exe = mpienv.util.decode(os.path.realpath(exe))
    return exe


class MpiBase(object):
    def __init__(self, prefix, conf, name=None):
        self._prefix = prefix
        self._conf = conf
        self._name = name

    def to_dict(self):
        return {
            'active': self.is_active,
            'broken': self.is_broken,
            'conf_params': self.conf_params,
            'default_name': self.default_name,
            'mpicc': self.mpicc,
            'mpicxx': self.mpicxx,
            'mpiexec': self.mpiexec,
            'prefix': self.prefix,
            'symlink': self.is_symlink,
            'type': self.type_,
            'version': self.version,
        }

    @property
    def prefix(self):
        pref = self._prefix
        if os.path.islink(pref):
            pref = os.readlink(pref)
        return pref

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def conf_params(self):
        return self._conf_params

    @property
    def version(self):
        return self._version

    @property
    def default_name(self):
        return self._default_name

    @property
    def mpiexec(self):
        ex = os.path.join(self.prefix, 'bin', 'mpiexec')
        return os.path.realpath(ex)

    @property
    def mpicxx(self):
        ex = os.path.join(self.prefix, 'bin', 'mpicxx')
        return os.path.realpath(ex)

    @property
    def mpicc(self):
        ex = os.path.join(self.prefix, 'bin', 'mpicc')
        return os.path.realpath(ex)

    @property
    def is_symlink(self):
        if self._name is None:
            raise RuntimeError("Internal Error:"
                               "is_symlink is not allowed for "
                               "non-installed MPI")
        return os.path.join(self._conf['mpi_dir'], self.name)

    @property
    def is_active(self):
        ex1 = self.mpiexec
        ex2 = _which('mpiexec')

        if ex2 is None or not os.path.exists(ex2):
            return False

        if os.path.islink(ex1):
            ex1 = os.readlink(ex1)
        if os.path.islink(ex2):
            ex2 = os.readlink(ex2)

        return ex1 == ex2

    @property
    def is_broken(self):
        return False

    def _mirror_file(self, f, dst_dir):
        dst = os.path.join(dst_dir, os.path.basename(f))

        if os.path.islink(f):
            src = os.path.realpath(f)
            os.symlink(src, dst)
        elif os.path.isdir(f):
            src = f
            os.symlink(src, dst)
        else:
            # ordinary files
            src = f
            os.symlink(src, dst)

    @property
    def type_(self):
        return self._type

    def bin_files(self):
        assert False, "Must be overriden"

    def inc_files(self):
        assert False, "Must be overriden"

    def lib_files(self):
        assert False, "Must be overriden"

    def libexec_files(self):
        assert False, "Must be overriden"

    def exec_(self):
        assert False, "Must be overriden"

    def run_cmd(self, cmd, extra_envs):
        envs = os.environ.copy()
        envs.update(extra_envs)
        # sys.stderr.write("MpiBase::run_cmd(): {}\n".format(' '.join(cmd)))
        p = Popen(cmd, env=envs)
        p.wait()
        exit(p.returncode)

    def use(self, name, mpi4py=False):
        # Defined in child classes (Mpich, Mvapich, OpenMPI ,etc)
        bin_files = self.bin_files()
        lib_files = self.lib_files()
        inc_files = self.inc_files()
        libexec_files = self.libexec_files()

        # sys.stderr.write("use: self={}\n".format(self))
        shim = self._conf['shims_dir']
        if os.path.exists(shim):
            shutil.rmtree(shim)

        os.mkdir(shim)

        for d in ['bin', 'lib', 'include', 'libexec']:
            dr = os.path.join(self._conf['shims_dir'], d)
            if not os.path.exists(dr):
                os.mkdir(dr)

        for f in bin_files:
            self._mirror_file(f, os.path.join(shim, 'bin'))

        for f in lib_files:
            self._mirror_file(f, os.path.join(shim, 'lib'))

        for f in inc_files:
            self._mirror_file(f, os.path.join(shim, 'include'))

        for f in libexec_files:
            self._mirror_file(f, os.path.join(shim, 'libexec'))

        if mpi4py:
            mpi4py = MPI4Py(self._conf, name)
            if not mpi4py.is_installed():
                mpi4py.install()
            mpi4py.use()

    def is_installed_by_mpienv(self):
        if self._name is None:
            return False
        mpi_prefix = os.path.abspath(os.path.join(self.prefix, os.pardir))
        return mpi_prefix == self._conf['mpi_dir']

    def remove(self):
        assert self._name is not None
        if self.is_installed_by_mpienv():
            shutil.rmtree(self.prefix)
        else:
            os.remove(os.path.join(self._conf['mpi_dir'], self.name))
