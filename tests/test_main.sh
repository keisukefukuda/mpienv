set -u

if [ -n "${ZSH_VERSION:-}" ]; then
    setopt shwordsplit
    SHUNIT_PARENT=$0
fi

declare -r test_dir=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
declare -r proj_dir=$(cd ${test_dir}/..; pwd)
declare -r MPICH=mpich-3.2
declare -r OMPI=openmpi-2.1.1

old_wd=$PWD

echo "proj_dir=$proj_dir"

cd ${test_dir}

if [ ! -d "${test_dir}/shunit2" ] ; then
    git clone https://github.com/kward/shunit2.git ${test_dir}/shunit2
fi

export MPIENV_VERSIONS_DIR=${HOME}/.mpienv-test-ver
echo MPIENV_VERSIONS_DIR=${MPIENV_VERSIONS_DIR}

export MPIENV_BUILD_DIR=${HOME}/.mpienv-build
echo MPIENV_BUILD_DIR=${HOME}/.mpienv-build

export MPIENV_CACHE_DIR=${HOME}/.mpienv-cache
echo MPIENV_CACHE_DIR=${HOME}/.mpienv-cache

export PIP_DOWNLOAD_CACHE=$HOME/.pip_download_cache
mkdir -p ${PIP_DOWNLOAD_CACHE}

rm -rf "$MPIENV_VERSIONS_DIR" |:
rm -rf "$MPIENV_CACHE_DIR" |:

oneTimeSetUp() {
    rm -rf ${MPIENV_VERSIONS_DIR}
    mkdir -p ${MPIENV_VERSIONS_DIR}
}

oneTimeTearDown() {
    rm -rf ${MPIENV_VERSIONS_DIR}
}

install_mpich() {
    export MPIENV_CONFIGURE_OPTS="--disable-fortran"
    mpienv install ${MPICH} >/dev/null 2>&1
}

install_ompi() {
    export MPIENV_CONFIGURE_OPTS="--disable-mpi-fortran"
    mpienv install ${OMPI} >/dev/null 2>&1
}

#-----------------------------------------------------------
export MPIENV_CONFIGURE_OPTS="--disable-fortran"
if [ ! -f "${MPIENV_BUILD_DIR}/${MPICH}/src/pm/hydra/mpiexec.hydra" ]; then
    echo "Building ${MPICH}"
    #mpienv build ${MPICH}
fi


export MPIENV_CONFIGURE_OPTS="--disable-mpi-fortran --disable-oshmem"
if [ ! -f "${MPIENV_BUILD_DIR}/${OMPI}/orte/tools/orterun/.libs/orterun" ]; then
    echo "Building ${OMPI}"
    #mpienv build ${OMPI} >/dev/null 2>&1
fi

# Load mpienv
. ${proj_dir}/init

#-----------------------------------------------------------
xtest_qc() {
    autopep8 --exclude pylib --diff -r . --global-config .pep8 | tee check_autopep8
    test ! -s check_autopep8
    assertEquals 0 $?

    flake8 $(find . -name "*.py" | grep -v pylib)
    assertEquals 0 $?
}

xtest_empty_list() {
    # There should  be nothing in MPIENV_VERSIONS_DIR
    mpienv list
    local LEN=$(mpienv list | wc -c)
    assertEquals 0 $LEN
}

xtest_1mpi() {
    # Test installing a single MPI,
    # and several operations on it.
    install_mpich

    mpienv list | grep -q ${MPICH}
    assertEquals 0 $?

    # Test json output
    mpienv list --json | python -c "import json;import sys; json.load(sys.stdin)"
    assertEquals 0 $?


    # Test rename
    # rename ${MPICH} -> my-cool-mpi
    mpienv rename ${MPICH} my-cool-mpi
    assertTrue "$?"
    mpienv list | grep -qE 'my-cool-mpi'
    assertTrue "$?"

    mpienv list | grep -qE ${MPICH}
    assertFalse "$?"

    # Rename back to ${MPICH}
    mpienv rename my-cool-mpi ${MPICH}
    mpienv list | grep -qE ${MPICH}
    assertTrue "$?"

    # Remove ${MPICH}
    install_ompi
    mpienv use ${OMPI}
    mpienv rm ${MPICH}
    assertTrue "$?"

    mpienv list | grep -q ${MPICH}
    assertFalse "$?"
}

xtest_2mpis() {
    install_mpich
    install_ompi

    mpienv list | grep -qE ${MPICH}
    assertTrue "$?"

    mpienv list | grep -qE "${OMPI}"
    assertTrue "$?"
}

get_key() {
    key=$1
    python -c "import json;import sys; print(json.load(sys.stdin)['${key}'])"
}

has_key() {
    key=$1
    python -c "import json;import sys; print(0 if '${key}' in json.load(sys.stdin) else 1)"
}

xtest_info() {
    install_mpich

    mpienv use ${MPICH}

    mpienv info ${MPICH} --json >a.json
    mpienv info --json >b.json

    diff -q a.json b.json >/dev/null
    assertTrue "$?"

    rm -f a.json b.json

    assertEquals "False" $(mpienv info --json | get_key "broken")
    assertEquals "MPICH" $(mpienv info --json | get_key "type")
    assertEquals "3.2"   $(mpienv info --json | get_key "version")
    assertTrue $(mpienv info --json | has_key "symlink")
    assertTrue $(mpienv info --json | has_key "mpiexec")
    assertTrue $(mpienv info --json | has_key "mpicc")
    assertTrue $(mpienv info --json | has_key "mpicxx")
    assertTrue $(mpienv info --json | has_key "default_name")
    assertTrue $(mpienv info --json | has_key "prefix")

    test -d "$(mpienv prefix)"
    assertTrue "$?"
}

xtest_mpi4py() {
    export TMPDIR=/tmp
    
    local SCRIPT=$(mktemp)
    cat <<EOF >$SCRIPT
from mpi4py import MPI
import sys
#print(MPI.__file__)
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
for i in range(0, comm.Get_size()):
    if i == rank:
        sys.stdout.write(str(rank))
        sys.stdout.flush()
    comm.barrier()
EOF
    # test Mpich
    install_mpich
    
    mpienv use --mpi4py ${MPICH}
    mpienv exec -n 2 python -c "from mpi4py import MPI"
    assertTrue $?
    OUT=$(mpienv use --mpi4py ${MPICH}; mpienv exec -n 2 python $SCRIPT)
    assertEquals "01" "$OUT"

    # test Open MPI
    install_ompi
    mpienv use --mpi4py ${OMPI}
    mpienv exec -n 2 python -c "from mpi4py import MPI"
    assertTrue $?
    OUT=$(mpienv use --mpi4py ${OMPI}; mpienv exec -n 2 python $SCRIPT)
    assertEquals "01" "$OUT"
    
    rm -f ${SCRIPT}
}

test_mpi4py_clear_pypath() {
    install_mpich

    unset PYTHONPATH
    assertNull "${PYTHONPATH:-}"

    #mpienv use ${MPICH}
    #assertNull "${PYTHONPATH:-}"

    #mpienv use --mpi4py ${MPICH}
    #assertNotNull "${PYTHONPAHT:-}"

    #mpienv use ${MPICH}
    #$assertNull "${PYTHONPATH:-}"
}

#-----------------------------------------------------------
# call shunit2
cd ${old_wd}

. ${test_dir}/shunit2/source/2.1/src/shunit2

