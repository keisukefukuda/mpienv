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

test_1mpi() {
    # Test installing a single MPI,
    # and several operations on it.
    mpienv install mpich-3.2 >/dev/null 2>&1

    mpienv list | grep -qE 'mpich-3.2'
    assertEquals 0 $?

    mpienv list | grep -qE 'openmpi'
    assertEquals 1 $?

    # Test json output
    mpienv list --json | python -c "import json;import sys; json.load(sys.stdin)"
    assertEquals 0 $?

    # Test rename
    # rename mpich-3.2 -> my-cool-mpi
    mpienv rename mpich-3.2 my-cool-mpi
    mpienv list | grep -qE 'my-cool-mpi'
    assertTrue $?

    mpienv list | grep -qE 'mpich-3.2'
    assertFalse $?

    # Rename back to mpich-3.2
    mpienv rename my-cool-mpi mpich-3.2
    mpienv list | grep -qE 'mpich-3.2'
    assertTrue $?

    # Remove mpich-3.2
    mpienv install openmpi-2.1.1 >/dev/null 2>&1
    mpienv use openmpi-2.1.1
    mpienv rm mpich-3.2
    assertTrue $?

    mpienv list | grep -q mpich-3.2
    assertFalse $?
}

test_2mpis() {
    mpienv install mpich-3.2 >/dev/null 2>&1
    mpienv install openmpi-2.1.1 >/dev/null 2>&1

    mpienv list | grep -qE 'mpich-3.2'
    assertTrue $?

    mpienv list | grep -qE 'openmpi-2.1.1'
    assertTrue $?
}

get_key() {
    key=$1
    python -c "import json;import sys; print(json.load(sys.stdin)['${key}'])"
}

test_info() {
    mpienv install mpich-3.2 >/dev/null 2>&1
    mpienv use mpich-3.2

    mpienv info mpich-3.2 --json >a.json
    mpienv info --json >b.json

    diff -q a.json b.json >/dev/null
    assertTrue $?

    rm -f a.json b.json

    assertEquals "False" "$(mpienv info --json | get_key "broken")"
}

#-----------------------------------------------------------
# call shunit2
cd ${old_wd}
. ${test_dir}/shunit2/source/2.1/src/shunit2

