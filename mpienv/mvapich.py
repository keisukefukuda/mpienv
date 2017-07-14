from mpienv import mpibase


class Mvapich(mpibase.MpiBase):
    def __init__(self, prefix, conf):
        super(Mvapich, self).__init__(prefix, conf)
