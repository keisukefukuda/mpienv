set -u

declare -r test_dir=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
declare -r proj_dir=$(cd ${test_dir}/..; pwd)

old_wd=$PWD

echo "proj_dir=$proj_dir"

cd ${test_dir}

if [ ! -d "${test_dir}/shunit2" ] ; then
    git clone https://github.com/kward/shunit2.git ${test_dir}/shunit2
fi

export MPIENV_VERSIONS_DIR=${HOME}/.mpienv-test
echo MPIENV_VERSIONS_DIR=${MPIENV_VERSIONS_DIR}

export MPIENV_BUILD_DIR=${HOME}/.mpienv-build
echo MPIENV_BUILD_DIR=${HOME}/.mpienv-build

export MPIENV_CACHE_DIR=${HOME}/.mpienv-cache
echo MPIENV_CACHE_DIR=${HOME}/.mpienv-cache


oneTimeSetUp() {
    rm -rf ${MPIENV_VERSIONS_DIR}
    mkdir -p ${MPIENV_VERSIONS_DIR}
}

oneTimeTearDown() {
    rm -rf ${MPIENV_VERSIONS_DIR}
}

# Load mpienv
. ${proj_dir}/init

#-----------------------------------------------------------
export MPIENV_CONFIGURE_OPTS="--disable-fortran"
if [ ! -f "${MPIENV_BUILD_DIR}/mpich-3.2/src/pm/hydra/mpiexec.hydra" ]; then
    echo "Building mpich-3.2"
    mpienv build mpich-3.2
fi


export MPIENV_CONFIGURE_OPTS="--disable-mpi-fortran --disable-oshmem"
if [ ! -f "${MPIENV_BUILD_DIR}/openmpi-2.1.1/orte/tools/orterun/.libs/orterun" ]; then
    echo "Building openmpi-2.1.1"
    mpienv build openmpi-2.1.1
fi

#-----------------------------------------------------------
test_empty_list() {
    # There should  be nothing in MPIENV_VERSIONS_DIR
    local LEN=$(mpienv list | wc -c)
    assertEquals 0 $LEN
}

test_install() {
    mpienv install mpich-3.2 >/dev/null 2>&1

    mpienv list | grep -qE 'mpich-3.2'
    assertEquals 0 $?

    mpienv list | grep -qE 'openmpi'
    assertEquals 1 $?
}

#-----------------------------------------------------------
# call shunit2
cd ${old_wd}
. ${test_dir}/shunit2/source/2.1/src/shunit2

