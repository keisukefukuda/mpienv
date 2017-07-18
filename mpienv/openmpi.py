# coding: utf-8
import os.path
from subprocess import check_output

from mpienv import mpibase
from mpienv.ompi import parse_ompi_info
from mpienv import util


def _call_ompi_info(bin):
    out = check_output([bin, '--all', '--parsable'], stderr=util.DEVNULL)
    out = util.decode(out)

    return parse_ompi_info(out)


class OpenMPI(mpibase.MpiBase):
    def __init__(self, prefix, conf):
        super(OpenMPI, self).__init__(prefix, conf)

        self._type = 'Open MPI'

        ompi = _call_ompi_info(os.path.join(self.prefix,
                                            'bin', 'ompi_info'))

        ver = ompi.get('ompi:version:full')
        mpi_ver = ompi.get('mpi-api:version:full')

        if os.path.islink(prefix):
            prefix = os.path.realpath(prefix)

        self._type = 'Open MPI'
        self._version = ver
        self._mpi_version = mpi_ver
        self._conf_params = []  # TODO(keisukefukuda)
        self._default_name = "openmpi-{}".format(ver)
        self._c = ompi.get('bindings:c')
        self._cxx = ompi.get('bindings:cxx')
        self._fortran = ompi.get('bindings:mpif.h')
        self._default_name = "openmpi-{}".format(ver)

        self._cuda = ompi.get(
            'mca:opal:base:param:opal_built_with_cuda_support')

    def bin_files(self):
        return util.glob_list([self.prefix, 'bin'],
                              ['mpi*',
                               'ompi-*',
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

    def exec_(self, cmds):
        envs = {}
        for v in ['PYTHONPATH', 'PATH', 'LD_LIBRARY_PATH']:
            cmds[:0] = ['-x', v]

        pref = self.prefix
        cmds[:0] = ['-prefix', pref]

        cmds[:0] = [self.mpiexec]

        self.run_cmd(cmds, envs)
