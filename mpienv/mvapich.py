# coding: utf-8
import os.path
import re
from subprocess import check_output

import mpienv.mpich as mpich
import mpienv.util as util


class Mvapich(mpich.Mpich):
    def __init__(self, *args):
        super(Mvapich, self).__init__(*args)

        self._type = 'MVAPICH'
        mpi_h = mpich.find_mpi_h(self.mpiexec)
        if not os.path.exists(mpi_h):
            raise RuntimeError("Error: Cannot find {}".format(mpi_h))

        mv_ver = check_output(['grep', '-E',
                               'define *MVAPICH2_VERSION', mpi_h],
                              stderr=util.DEVNULL)
        mch_ver = check_output(['grep', '-E',
                                'define *MPICH_VERSION', mpi_h],
                               stderr=util.DEVNULL)

        mv_ver = util.decode(mv_ver)
        mch_ver = util.decode(mch_ver)

        mv_ver = re.search(r'"([.0-9]+(a\d*|b\d*|rc\d*)?)"', mv_ver).group(1)
        mch_ver = re.search(r'"([.0-9]+)"', mch_ver).group(1)

        self._version = mv_ver
        self._mpich_ver = mch_ver
        self._default_name = "mvapich2-{}".format(mv_ver)

    def libexec_files(self):
        return util.glob_list([self.prefix, 'libexec'],
                              ['osu-micro-benchmarks'])
