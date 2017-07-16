from mpienv import mpibase
from mpienv import util


class OpenMPI(mpibase.MpiBase):
    def __init__(self, prefix, conf):
        super(OpenMPI, self).__init__(prefix, conf)

    def bin_file(self):
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
