#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv) {
  int rank, size, i;
  MPI_Init(&argc, &argv);

  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);

  if (rank == 0) {
    printf("size %d\n", size);
    fflush(stdout);
  }

  for (i = 0; i < size; i++) {
    if (rank == i) {
      printf("Rank %d\n", i);
      fflush(stdout);
    }
    MPI_Barrier(MPI_COMM_WORLD);
  }
  
  MPI_Finalize();
}
