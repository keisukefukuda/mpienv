from mpienv import mpibase


class OpenMPI(mpibase.MpiBase):
    def __init__(self, prefix, conf):
        super(OpenMPI, self).__init__(prefix, conf)
