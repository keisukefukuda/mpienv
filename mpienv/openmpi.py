# coding: utf-8
from mpienv import mpibase
from mpienv import util


class OpenMPI(mpibase.MpiBase):
    def __init__(self, prefix, conf):
        super(OpenMPI, self).__init__(prefix, conf)

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
        # TODO(keisukefukuda) Implement --prefix option for OpenMPI
        cmds[:0] = ['-prefix', pref]

        cmds[:0] = [self.mpiexec]

        self.run_cmd(cmds, envs)
