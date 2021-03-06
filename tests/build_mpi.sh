#!/bin/bash

set -e

function install_ompi {
    MPI=$1
    VER=$(echo "$MPI" | grep -Eo "[0-9.]+$")
    MAJOR=$(echo "$VER" | grep -Eo "^[0-9]+\.[0-9]+")
    DIST="https://download.open-mpi.org/release/open-mpi/v${MAJOR}/openmpi-${VER}.tar.bz2"

    PREFIX=$HOME/mpi/$MPI
    FILE=$(basename $DIST)

    echo PREFIX=$PREFIX
    echo DIST=$DIST

    echo "-------------------------------------------------"
    echo "Installing $1"
    echo "-------------------------------------------------"

    if [ ! -x $PREFIX/bin/mpicxx ]; then
        rm -rf $BUILD_DIR/*
        cd $BUILD_DIR
        mkdir -p $PREFIX
        # Download the archive
        RETRY_COUNT=0
        while [ "$RETRY_COUNT" -lt 5 ]; do
            if md5sum -c ${CHECKSUM} 2>/dev/null | grep -q "${FILE}: OK"; then
                break
            else
                if [ -f "${FILE}" ]; then
                    echo "MD5 mismatch:"
                    file ${FILE}
                    md5sum ${FILE}
                    echo "Answer is:"
                    cat ${CHECKSUM}
                fi
                rm -f ${FILE}
                sleep 2
                echo curl -OL "${DIST}"
                curl -OL "${DIST}"
                RETRY_COUNT=$(expr ${RETRY_COUNT} + 1)
            fi
        done

        if [ "$RETRY_COUNT" -eq 5 ]; then
            echo "Error : failed to download $FILE" >&2
            exit 1
        fi
        
        tar -xf $FILE
        cd $(find . -maxdepth 1 -mindepth 1 -type d)
        ./configure --prefix=$PREFIX \
                    --disable-mpi-fortran \
                    --enable-mpi-cxx \
                    --enable-shared=yes
        make -j4 && make install
    fi

    $PREFIX/bin/mpicxx --showme:version
}

function install_mpich {
    MPI=$1
    VER=$(echo "$MPI" | grep -Eo "[0-9.]+$")
    DIST="http://www.mpich.org/static/downloads/${VER}/mpich-${VER}.tar.gz"
    PREFIX=$HOME/mpi/$MPI
    FILE=$(basename $DIST)

    echo PREFIX=$PREFIX
    echo DIST=$DIST

    echo "-------------------------------------------------"
    echo "Installing $1"
    echo "-------------------------------------------------"

    if [ ! -x $PREFIX/bin/mpicxx ]; then
        rm -rf $BUILD_DIR/*
        cd $BUILD_DIR
        mkdir -p $PREFIX

        # Download the archive
        RETRY_COUNT=0
        while [ "$RETRY_COUNT" -lt 5 ]; do
            if md5sum -c ${CHECKSUM} 2>/dev/null | grep -q "${FILE}: OK"; then
                break
            else
                if [ -f "${FILE}" ]; then
                    echo "MD5 mismatch:"
                    file ${FILE}
                    md5sum ${FILE}
                    echo "Answer is:"
                    cat ${CHECKSUM}
                fi
                rm -f ${FILE}
                sleep 2
                curl -L ${DIST} >${FILE}
                RETRY_COUNT=$(expr ${RETRY_COUNT} + 1)
            fi
        done

        if [ "$RETRY_COUNT" -eq 5 ]; then
            echo "Error : failed to download $FILE" >&2
            exit 1
        fi
          

        tar -xf $FILE
        cd $(find . -maxdepth 1 -mindepth 1 -type d)
        ./configure --prefix=$PREFIX \
                    --disable-f77 --disable-fc\
                    --enable-cxx \
                    --enable-shared=yes
        make -j4 && make install
    fi

    $PREFIX/bin/mpicxx -show
}


if [ "$(uname)" == "Darwin" ]; then
  SELF="$(readlink $0 || echo $0)"
  TEST_DIR=$(dirname $SELF)
else
  TEST_DIR=$(dirname $(readlink -e $0))
fi

echo TEST_DIR=$TEST_DIR
PROJ_DIR=$(cd ${TEST_DIR}/..; pwd -P)
CHECKSUM=$(cd $TEST_DIR; pwd)/md5checksum.txt

BUILD_DIR=$HOME/mpi-build
mkdir -p ~/mpi
mkdir -p $BUILD_DIR

install_ompi openmpi-3.1.2
install_mpich mpich-3.0.4
