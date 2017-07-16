from mpienv import mpibase
from mpienv import util


class Mpich(mpibase.MpiBase):
    def __init__(self, prefix, conf):
        super(Mpich, self).__init__(prefix, conf)

    def bin_file(self):
        return util.glob_list([self.prefix, 'bin'],
                              ['hydra_*',
                               'mpi*',
                               'parkill'])

    def lib_files(self):
        return util.glob_list([self.prefix, 'lib'],
                              ['lib*mpi*.*',
                               'lib*mpl*.*',
                               'libopa.*'])

    def inc_files(self):
        return util.glob_list([self.prefix, 'include'],
                              ['mpi*.h',
                               'mpi*.mod',
                               'opa*.h',
                               'primitives'])
