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
    def __init__(self, prefix, mpiexec, mpicc,
                 inc_dir, lib_dir,
                 conf, name=None):
        self._prefix = prefix
        self._mpiexec = mpiexec
        self._mpicc = mpicc
        self._inc_dir = inc_dir
        self._lib_dir = lib_dir
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
    def conf(self):
        return self._conf

    @property
    def version(self):
        return self._version

    @property
    def default_name(self):
        return self._default_name

    @property
    def mpiexec(self):
        return self._mpiexec

    @property
    def mpicxx(self):
        return self.mpicc.replace('mpicc', 'mpicxx')

    @property
    def mpicc(self):
        return self._mpicc

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

        ex1 = os.path.realpath(ex1)
        ex2 = os.path.realpath(ex2)

        return ex1 == ex2

    @property
    def is_broken(self):
        return False

    def _mirror_file(self, f, dst_dir, dst_bname=None):
        if dst_bname is None:
            dst = os.path.join(dst_dir, os.path.basename(f))
        else:
            dst = os.path.join(dst_dir, dst_bname)

        if os.path.islink(f):
            src = os.path.realpath(f)
            # sys.stderr.write("link {} -> {}\n".format(src, dst))
            os.symlink(src, dst)
        elif os.path.isdir(f):
            src = f
            # sys.stderr.write("link {} -> {}\n".format(src, dst))
            os.symlink(src, dst)
        else:
            # ordinary files
            src = f
            # sys.stderr.write("link {} -> {}\n".format(src, dst))
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

        shimd = self.conf['shims_dir']
        ld_lib_path = "{}/lib:{}/lib64".format(shimd, shimd)

        # We need to construct LD_LIBRARY_PATH for the child mpiexec process
        # because setuid-ed programs ignore 'LD_LIBRARY_PATH'.
        if 'LD_LIBRARY_PATH' in envs:
            ld_lib_path = envs['LD_LIBRARY_PATH'] + ":" + ld_lib_path

        envs['LD_LIBRARY_PATH'] = ld_lib_path

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
            if os.path.islink(shim):
                os.unlink(shim)
            else:
                try:
                    shutil.rmtree(shim)
                except OSError:
                    os.unlink(shim)

        os.mkdir(shim)

        for d in ['bin', 'lib', 'include', 'libexec']:
            dr = os.path.join(self._conf['shims_dir'], d)
            if not os.path.exists(dr):
                os.mkdir(dr)

        for f in bin_files:
            bin = os.path.join(shim, 'bin')
            self._mirror_file(f, bin)
        self._mirror_file(self.mpiexec, bin, 'mpiexec')
        self._mirror_file(self.mpicc, bin, 'mpicc')
        self._mirror_file(self.mpicxx, bin, 'mpicxx')

        for f in lib_files:
            self._mirror_file(f, os.path.join(shim, 'lib'))

        for f in inc_files:
            self._mirror_file(f, os.path.join(shim, 'include'))

        for f in libexec_files:
            self._mirror_file(f, os.path.join(shim, 'libexec'))

        py = MPI4Py(self._conf, name)
        if mpi4py:
            if not py.is_installed():
                py.install()
            py.use()
        else:
            # If --mpi4py is not specified, must modify PYTHONPATH
            # to remove mismatched path to mpi4py module
            py.clear()

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
