# coding: utf-8
import os.path
import re
from subprocess import check_output

import mpienv.mpibase as mpibase
from mpienv.ompi import parse_ompi_info
import mpienv.util as util


def _call_ompi_info(bin):
    out = check_output([bin, '--all', '--parsable'], stderr=util.DEVNULL)
    out = util.decode(out)

    return parse_ompi_info(out)


class OpenMPI(mpibase.MpiBase):
    def __init__(self, mpiexec, conf, name=None):
        # `mpiexec` might be 'mpiexec' or 'mpiexec.ompi'
        mpicc = re.sub('mpiexec', 'mpicc', mpiexec)
        assert os.path.exists(mpicc)
        prefix = os.path.abspath(
            os.path.join(os.path.dirname(mpiexec), os.path.pardir))
        ompi_info = os.path.join(prefix, 'bin', 'ompi_info')

        info = _call_ompi_info(ompi_info)

        inc_dir = info.get('path:incdir')
        lib_dir = info.get('path:libdir')

        super(OpenMPI, self).__init__(prefix, mpiexec, mpicc,
                                      inc_dir, lib_dir, conf, name)

        self._type = 'Open MPI'

        ver = info.get('ompi:version:full')
        mpi_ver = info.get('mpi-api:version:full')

        self._type = 'Open MPI'
        self._version = ver
        self._mpi_version = mpi_ver
        # Open MPI does not provide a way to get configure params
        self._conf_params = {}
        self._default_name = "openmpi-{}".format(ver)
        self._c = info.get('bindings:c')
        self._cxx = info.get('bindings:cxx')
        self._fortran = info.get('bindings:mpif.h')
        self._default_name = "openmpi-{}".format(ver)

        self._cuda = info.get(
            'mca:opal:base:param:opal_built_with_cuda_support')

    def bin_files(self):
        return util.glob_list([self.prefix, 'bin'],
                              ['ompi-*',
                               'ompi_*',
                               'orte*',
                               'opal_'])

    def lib_files(self):
        return util.glob_list([self.prefix, 'bin'],
                              ['libmpi*',
                               'libmca*',
                               'libompi*',
                               'libopen-pal*',
                               'libopen-rte*',
                               'openmpi',
                               'pkgconfig'])

    def inc_files(self):
        return util.glob_list([self.prefix, 'include'],
                              ['mpi*.h', 'openmpi'])

    def libexec_files(self):
        return []
