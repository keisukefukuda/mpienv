#!/bin/sh

mkdir -p $HOME/mpi
mkdir -p $HOME/tmp


# Install zsh
if [ -x $HOME/zsh/bin/zsh ]; then
    rm -f --no-check-certificate
    rm -rf zsh  # clear zsh/ directory
    
    mkdir $HOME/zsh
    wget --no-check-certificate 'https://downloads.sourceforge.net/project/zsh/zsh/5.3.1/zsh-5.3.1.tar.gz?r=http%3A%2F%2Fzsh.sourceforge.net%2FArc%2Fsource.html&ts=1495843150&use_mirror=jaist' -O zsh-5.3.1.tar.gz

    tar -xf zsh-5.3.1.tar.gz
    cd zsh-5.3.1
    ./configure --prefix=$HOME/zsh
    make -j2
    make install
    cd
fi


PREFIX=$HOME/mpi

# Open MPI 2.1.1
cd $HOME/tmp

ls $PREFIX

for VER in 2.1.1 1.10.7; do
    if [ ! -x $PREFIX/openmpi-${VER}/bin/mpiexec ]; then
        echo "==============================================="
        echo "Installing Open MPI ${VER}"
        echo "==============================================="
        VER_SHORT=$(echo $VER | grep -oE '^[0-9]+\.[0-9]+')
        wget --no-check-certificate https://www.open-mpi.org/software/ompi/v${VER_SHORT}/downloads/openmpi-${VER}.tar.gz
        tar -xf openmpi-${VER}.tar.gz
        cd openmpi-${VER}
        ./configure --prefix=$PREFIX/openmpi-${VER} --disable-mpi-fortran
        make -j4
        make install
        cd ..
    else
        echo "Open MPI ${VER} looks good."
        $PREFIX/openmpi-${VER}/bin/mpiexec --version
    fi
    echo
    echo
done

# MPICH
cd $HOME/tmp
for VER in 3.2; do
    if [ ! -x $PREFIX/mpich-${VER}/bin/mpiexec ]; then
        echo "==============================================="
        echo "Installing MPICH ${VER}"
        echo "==============================================="
        wget --no-check-certificate http://www.mpich.org/static/downloads/${VER}/mpich-${VER}.tar.gz
        tar -xf mpich-${VER}.tar.gz
        cd mpich-${VER}
        ./configure --disable-fortran --prefix=$PREFIX/mpich-${VER}
        make -j4
        make install
        cd ..
    else
        echo "MPICH ${VER} looks good."
        $PREFIX/mpich-${VER}/bin/mpiexec --version
    fi
    echo
    echo
done

# MVAPICH
cd $HOME/tmp
for VER in 2.2; do
    if [ ! -x $PREFIX/mvapich2-2.2/bin/mpiexec ]; then
        echo "==============================================="
        echo "Installing MVAPICH ${VER}"
        echo "==============================================="
        wget --no-check-certificate http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-${VER}.tar.gz
        tar -xf mvapich2-${VER}.tar.gz
        cd mvapich2-${VER}
        ./configure --disable-fortran --prefix=$PREFIX/mvapich2-2.2 --disable-mcast
        make -j4
        make install
        cd ..
    else
        echo "MPVAPICH ${VER} looks good."
        $PREFIX/mvapich2-2.2/bin/mpiexec --version
    fi
    echo
    echo
done
