# coding: utf-8

import os.path
import shutil

from mpienv.py import MPI4Py


class MpiBase(object):
    def __init__(self, prefix, conf):
        self._prefix = prefix
        self._conf = conf

    @property
    def prefix(self):
        return self._prefix

    @property
    def mpiexec(self):
        ex = os.path.join(self._prefix, 'bin', 'mpiexec')
        if os.path.islink(ex):
            ex2 = os.readlink(ex)
            if not os.path.isabs(ex2):
                ex2 = os.path.join(os.path.dirname(ex), ex2)

        return ex2

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

    def bin_files(self):
        assert False, "Must be overriden"

    def inc_files(self):
        assert False, "Must be overriden"

    def lib_files(self):
        assert False, "Must be overriden"

    def libexec_files(self):
        assert False, "Must be overriden"

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
