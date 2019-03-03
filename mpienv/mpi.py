# coding: utf-8

import os.path
import re
from subprocess import call
from subprocess import PIPE
from subprocess import Popen
import sys

import mpienv.mpich as mpich
import mpienv.mvapich as mvapich
import mpienv.openmpi as openmpi
import mpienv.util as util


try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


def _is_broken_symlink(path):
    return os.path.islink(path) and not os.path.exists(path)


class BrokenMPI(object):
    def __init__(self, mpiexec, conf, name=None):
        # assert os.path.islink(mpiexec)
        self._mpiexec = mpiexec
        self._conf = conf
        self._name = name

    @property
    def is_broken(self):
        return True

    def remove(self):
        link = os.path.join(self._conf['mpi_dir'], self._name)
        os.remove(link)


def get_mpi_class(mpienv, mpiexec):
    """Return the class of the MPI"""
    if not os.path.exists(mpiexec):
        # prefix directory does exist but prefix/bin/mpiexec
        # does not. --> It seems that the MPI has been
        # uninstalled after registered to mpienv?
        sys.stderr.write("'{}' seems to be broken because "
                         "there's no such file or directory\n".format(mpiexec))
        return BrokenMPI

    if _is_broken_symlink(mpiexec):
        return BrokenMPI

    # Add LD_LIBRARY_PATH
    bin_dir = os.path.dirname(mpiexec)
    lib_dir = os.path.abspath(os.path.join(bin_dir, os.pardir, 'lib'))

    env = os.environ.copy()
    ld_lib_path = [lib_dir] + env.get('LD_LIBRARY_PATH', '').split(':')
    env['LD_LIBRARY_PATH'] = ':'.join(ld_lib_path)

    p = Popen([mpiexec, '--version'], stderr=PIPE, stdout=PIPE, env=env)
    out, err = p.communicate()
    ver_str = util.decode(out + err)

    if re.search(r'OpenRTE', ver_str, re.MULTILINE):
        # Open MPI
        return openmpi.OpenMPI

    if re.search(r'HYDRA', ver_str, re.MULTILINE):
        # MPICH or MVAPICH
        # if mpi.h is installed, check it to identiy
        # the MPI type.
        # This is because MVAPCIH uses MPICH's mpiexec,
        # so we cannot distinguish them only from mpiexec.
        mpi_h = mpich.find_mpi_h(mpiexec, ver_str)
        ret = call(['grep', 'MVAPICH2_VERSION', '-q', mpi_h],
                   stderr=DEVNULL)
        if ret == 0:
            # MVAPICH
            return mvapich.Mvapich
        else:
            # MPICH
            # on some platform, sometimes only runtime
            # is installed and developemnt kit (i.e. compilers)
            # are not installed.
            # In this case, we assume it's mpich.
            return mpich.Mpich

    # Failed to detect MPI
    sys.stderr.write("ver_str = {}\n".format(ver_str))
    raise RuntimeError("Unknown MPI type '{}'".format(mpiexec))
