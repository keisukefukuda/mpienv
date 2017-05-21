#!/bin/sh

mkdir -p $HOME/mpi
mkdir -p $HOME/tmp
cd $HOME/tmp

PREFIX=$HOME/mpi

# Open MPI 2.1.1
for VER in 2.1.1 1.10.7; do
    if [ ! -x $PREFIX/openmpi-${VER}/bin/mpiexec ]; then
        VER_SHORT=$(echo $VER | grep -oE '^[0-9]+\.[0-9]+')
        wget https://www.open-mpi.org/software/ompi/v${VER_SHORT}/downloads/openmpi-${VER}.tar.gz
        tar -xf openmpi-${VER}.tar.gz
        cd openmpi-${VER}
        ./configure --prefix=$PREFIX/openmpi-${VER} --disable-mpi-fortran
        make -j4
        make install
        cd ..
    fi
done

# MPICH
for VER in 3.2; do
    if [ ! -x $PREFIX/mpich-${VER}/bin/mpiexec ]; then
        wget http://www.mpich.org/static/downloads/${VER}/mpich-${VER}.tar.gz
        tar -xf mpich-${VER}.tar.gz
        cd mpich-${VER}
        ./configure --disable-fortran --prefix=$PREFIX/mpich-${VER}
        make -j4
        make install
        cd ..
    fi
done

# MVAPICH
for VER in 2.2; do
    if [ ! -x $PREFIX/mvapich2-2.2/bin/mpiexec ]; then
        wget http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-${VER}.tar.gz
        tar -xf mvapich2-${VER}.tar.gz
        cd mvapich2-${VER}
        ./configure --disable-fortran --prefix=$PREFIX/mvapich2-2.2
        make -j4
        make install
        cd ..
    fi
done
