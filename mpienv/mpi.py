# coding: utf-8

import os.path
import re
from subprocess import call
from subprocess import PIPE
from subprocess import Popen
import sys

from mpienv import mpich
from mpienv import mvapich
from mpienv import openmpi
from mpienv import util


try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


def _find_mpich_mpi_h(ver_str):
    """Find mpi.h file from MPICH mpiexec binary"""
    line = next(ln for ln in ver_str.split("\n")
                if re.search(r'Configure options', ln))
    dir_cands = re.findall(r'--includedir=([^\' \n]+)', line)
    # print(dir_cands)
    inc_dir = next(p for p in dir_cands
                   if os.path.exists(os.path.join(p, 'mpi.h')))
    return os.path.join(inc_dir, 'mpi.h')


def _is_broken_symlink(path):
    return os.path.islink(path) and not os.path.exists(path)


class BrokenMPI(object):
    def __init__(self, mpiexec, conf, name=None):
        assert os.path.islink(mpiexec)
        self._mpiexec = mpiexec
        self._conf = conf
        self._name = name

    @property
    def is_broken(self):
        return True

    def remove(self):
        os.remove(self._mpiexec)


def MPI(mpienv, mpiexec):
    """Return the class of the MPI"""
    if not os.path.exists(mpiexec):
        prefix = os.path.abspath(
            os.path.join(os.path.dirname(mpiexec), os.pardir))
        if os.path.isdir(prefix):
            # prefix directory does exist but prefix/bin/mpiexec
            # does not. --> It seems that the MPI has been
            # uninstalled after registered to mpienv?
            return BrokenMPI
        else:
            sys.stderr.write("mpienv [Error]: no such directory: {}"
                             .format(prefix))
            return BrokenMPI

    if _is_broken_symlink(mpiexec):
        return BrokenMPI

    p = Popen([mpiexec, '--version'], stderr=PIPE, stdout=PIPE)
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
        mpi_h = _find_mpich_mpi_h(ver_str)
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
