from mpienv import mpich
from mpienv import util


class Mvapich(mpich.Mpich):
    def __init__(self, prefix, conf):
        super(Mvapich, self).__init__(prefix, conf)

    def libexec_files(self):
        return util.glob_list([self.prefix, 'libexec'],
                              ['osu-micro-benchmarks'])
