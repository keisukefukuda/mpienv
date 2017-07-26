from mpi4py import MPI
import sys
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
for i in range(0, comm.Get_size()):
    if i == rank:
        sys.stdout.write(str(rank))
        sys.stdout.flush()
    comm.Barrier()
