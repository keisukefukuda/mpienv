from mpienv import mpibase


class Mpich(mpibase.MpiBase):
    def __init__(self, prefix, conf):
        super(Mpich, self).__init__(prefix, conf)
