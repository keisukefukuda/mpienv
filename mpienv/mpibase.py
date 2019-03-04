# coding: utf-8

import distutils.spawn
import os.path
import shutil
from subprocess import Popen
import sys  # NOQA

from mpienv.py import MPI4Py
import mpienv.util as util


def _which(cmd):
    exe = distutils.spawn.find_executable(cmd)
    if exe is None:
        return None

    exe = util.decode(os.path.realpath(exe))
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

        env_path = os.environ.get('PATH', '').split(':')
        env_ldlib = os.environ.get('LIBRARY_PATH', '').split(':')

        # Remove all directory that contains 'mpiexec' from PATH
        bin_dir = os.path.join(self.prefix, 'bin')
        assert os.path.exists(os.path.join(bin_dir, 'mpiexec'))
        if bin_dir in env_path:
            env_path.remove(bin_dir)
        env_path = [bin_dir] + env_path

        # Remove all directory that contains 'mpiexec'
        for dir_name in ['lib', 'lib64']:
            lib_dir = os.path.join(self.prefix, dir_name)
            if os.path.exists(lib_dir):
                if lib_dir in env_ldlib:
                    env_ldlib.remove(lib_dir)
                env_ldlib = [lib_dir] + env_ldlib

        print('export PATH={}'.format(':'.join(env_path)))
        print('export LD_LIBRARY_PATH={}'.format(':'.join(env_ldlib)))

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
