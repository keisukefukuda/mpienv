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


try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


def _find_mpi_h(mpiexec):
    """Find mpi.h file from mpiexec/mpicc binary"""
    mpicc = re.sub(r'mpiexec', 'mpicc', mpiexec)

    if not os.path.exists(mpiexec):
        raise RuntimeError("Internal Error: mpicc not found")

    p = Popen([mpicc, '-show'], stdout=PIPE)
    out, err = p.communicate()

    m = re.search(r'-I(\S+)', out.decode(sys.getdefaultencoding()))
    if m is None:
        raise RuntimeError("Internal Error: mpicc -show does not include -I")

    cpath = m.group(1)

    mpi_h = os.path.join(cpath, 'mpi.h')
    return mpi_h


def _decode(s):
    if type(s) == bytes:
        return s.decode(sys.getdefaultencoding())
    else:
        return s


def _encode(s):
    if type(s) == str:
        return s.encode(sys.getdefaultencoding())
    else:
        return s


def _is_broken_symlink(path):
    return os.path.islink(path) and not os.path.exists(path)


class BrokenMPI(object):
    def __init__(self):
        pass

    @property
    def broken(self):
        return True


def MPI(mpiexec):
    """Return the class of the MPI"""
    # TODO(keisukefukuda): Handle macports MPIs
    if not os.path.exists(mpiexec):
        raise RuntimeError("Internal Error: mpiexec not found")

    if _is_broken_symlink(mpiexec):
        return BrokenMPI

    p = Popen([mpiexec, '--version'], stderr=PIPE, stdout=PIPE)
    out, err = p.communicate()
    ver_str = _decode(out + err)

    if re.search(r'OpenRTE', ver_str, re.MULTILINE):
        # Open MPI
        return openmpi.OpenMPI

    if re.search(r'HYDRA', ver_str, re.MULTILINE):
        # MPICH or MVAPICH
        # if mpi.h is installed, check it to identiy
        # the MPI type.
        # This is because MVAPCIH uses MPICH's mpiexec,
        # so we cannot distinguish them only from mpiexec.
        mpi_h = _find_mpi_h(mpiexec)
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
