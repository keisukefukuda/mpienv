#!/bin/bash
set -u
set -x

# ==============================================================
# Configuration
# ==============================================================
MPI_PREFIX=$HOME/mpi

if [ ! -d "${TMPDIR:-}" ]; then
  TMPDIR=/tmp/$USER/$$
  mdkir -p $TMPDIR
fi
export MPIENV_ROOT=$TMPDIR/mpienv/
echo MPIENV_ROOT=$MPIENV_ROOT

export PIP_DOWNLOAD_CACHE=$HOME/.pip_download_cache
mkdir -p ${PIP_DOWNLOAD_CACHE}

export PYTHON=$(which python)

export OMPI_MCA_btl_base_warn_component_unused=1

mkdir -p $MPIENV_ROOT
rm -rf $MPIENV_ROOT/* |:
rm -rf $MPIENV_ROOT/.* |:

# ==============================================================
# Dump INFO
# ==============================================================

date
hostname

# ==============================================================
# Setup
# ==============================================================


pip uninstall -y mpienv ||:

if [ -n "${ZSH_VERSION:-}" ]; then
    setopt shwordsplit
    SHUNIT_PARENT=$0
fi

declare -r test_dir=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
declare -r proj_dir=$(cd ${test_dir}/..; pwd)

old_wd=$PWD

echo "proj_dir=$proj_dir"

# Load mpienv
echo "=================== Install mpienv =================="
cd ${proj_dir}
rm -rf mpienv.egg-info dist ||:
python -m pip install -e .

echo "=================== Load mpienv =================="
INIT=$(which mpienv-init)

set +x
set +u
eval "$($INIT)"
set -u

echo "=================== Call mpienv =================="
mpienv list

cd ${test_dir}

if [ ! -d "${test_dir}/shunit2" ] ; then
    git clone https://github.com/kward/shunit2.git --branch v2.1.6 ${test_dir}/shunit2
fi

# ==============================================================
# Test functions
# ==============================================================

setUp() {
  export MPIENV_ROOT=$TMPDIR/mpienv/
  rm -rf $MPIENV_ROOT |:
  mkdir -p $MPIENV_ROOT
}

tearDown() {
  rm -rf $MPIENV_ROOT |:
}

assertSuccess() {
    ret=0
    $* || ret=$?
    assertTrue "'$*' Success" "$?"
}

is_ubuntu1404() {
    ret=0
    grep -q "Ubuntu 14.04" /etc/lsb-release 2>/dev/null || ret=$?
    return $ret
}

is_macos() {
    ret=0
    echo "$OSTYPE" | grep -qiE "^darwin" || ret=$?
    return $ret
}

echo "Running on Ubuntu 14.04"
export MPICH_VER=3.0.4
export MPICH_ROOT="$MPI_PREFIX/mpich-3.0.4"
export MPICH_EXEC="$MPICH_ROOT/bin/mpiexec"
export MPICH_CC_BIN="$MPICH_ROOT/bin/mpicc" # avoid MPICH_CC
export MPICH=mpich-${MPICH_VER}

export OMPI_VER=3.1.2
export OMPI_ROOT="$HOME/mpi/openmpi-3.1.2"
export OMPI_EXEC="$OMPI_ROOT/bin/mpiexec"
export OMPI_CC_BIN="$OMPI_ROOT/bin/mpicc"
export OMPI=openmpi-${OMPI_VER}

print_mpi_info() {
    unset tmpfile
    local tmpfile=$(mktemp "/tmp/${0##*/}.tmp.XXXXXX")
    local MPIEXEC=$1
    local INFO=$2
    cat <<EOF >${tmpfile}
from mpienv.mpi import get_mpi_class
from mpienv import mpienv
cls = get_mpi_class(mpienv, '${MPIEXEC}')
mpi = cls('${MPIEXEC}', mpienv.config())
print(mpi.${INFO})
EOF
    env PYTHONPATH=. python ${tmpfile}
    rm -f ${tmpfile}
}

#-----------------------------------------------------------
test_qc() {
    autopep8 --exclude pylib --diff -r . --global-config .pep8 | tee check_autopep8
    test ! -s check_autopep8
    assertEquals 0 $?

    flake8 --version
    flake8 $(find . -name "*.py" | grep -v pylib)
    assertEquals 0 $?
}

test_empty_list() {
    # There should  be nothing in MPIENV_VERSIONS_DIR
    echo MPIENV_ROOT=$MPIENV_ROOT
    ls -a $MPIENV_ROOT
    mpienv list
    local LEN=$(mpienv list | wc -c)
    assertEquals 0 $LEN
}

test_mpich_info() {
    local EXEC=$(print_mpi_info ${MPICH_EXEC} "mpiexec")
    assertEquals ${MPICH_EXEC} ${EXEC}

    local CC=$(print_mpi_info ${MPICH_EXEC}  "mpicc")
    assertEquals ${MPICH_CC_BIN} ${CC}

    local PREF=$(print_mpi_info ${MPICH_EXEC} "prefix")
    assertEquals ${MPICH_ROOT} "${PREF}"

    local VER=$(print_mpi_info ${MPICH_EXEC} "version")
    assertEquals ${MPICH_VER} ${VER}
}

test_openmpi_info() {
    local EXEC=$(print_mpi_info ${OMPI_EXEC} "mpiexec")
    assertEquals ${OMPI_EXEC} ${EXEC}

    local CC=$(print_mpi_info ${OMPI_EXEC} "mpicc")
    assertEquals ${OMPI_CC_BIN} ${CC}

    local PREF=$(print_mpi_info ${OMPI_EXEC} "prefix")
    assertEquals ${OMPI_ROOT} ${PREF}

    local VER=$(print_mpi_info ${OMPI_EXEC} "version")
    assertEquals ${OMPI_VER} ${VER}
}

test_1mpi() {
    # mpienv list
    mpienv autodiscover -q --add ${MPI_PREFIX}

    mpienv list | grep -q mpich-${MPICH_VER}
    assertTrue "$?"

    # Test json output
    mpienv list --json | python -m json.tool >/dev/null
    assertTrue "mpienv list --json produces proper JSON" "$?"

    # Test rename
    # rename mpich -> my-cool-mpi
    mpienv rename mpich-${MPICH_VER} my-cool-mpi
    assertTrue "rename my-cool-mpi" "$?"
    mpienv list | grep -qE 'my-cool-mpi'
    assertTrue "renamed" "$?"

    mpienv list | sed -e 's/->.*$//' | grep -q "mpich-${MPICH_VER}"
    assertFalse "mpich-${MPICH_VER} is renamed and disappeared." "$?"

    # Rename back to mpich
    mpienv rename my-cool-mpi mpich-${MPICH_VER}
    mpienv list | grep -q "mpich-${MPICH_VER}"
    assertTrue "rename my-cool-mpi back to mpich-${MPICH_VER} " "$?"

    # Remove mpich
    assertSuccess mpienv use openmpi-${OMPI_VER}  # Activate Open MPI to remove mpich
    assertSuccess mpienv rm mpich-${MPICH_VER}    # Remove mpich
    mpienv list | grep -q mpich-${MPICH_VER} # Check if it's removed
    assertFalse "remove mpich-${MPICH_VER}" "$?"  # Thus the grep should fail
}

json_get() {
    # Assuming a JSON dict is given from the stdin,
    # return the value of dict[key]
    key=$1
    python -c "import json;import sys; print(json.load(sys.stdin)['${key}'])"
}

json_check_key() {
    # Assuming a JSON dict is given from the stdin,
    # checks if dict has the key
    key=$1
    python -c "import json;import sys; print(0 if '${key}' in json.load(sys.stdin) else 1)"
}

test_cmd_info() {
    assertSuccess mpienv autodiscover -q --add ${MPI_PREFIX}
    mpienv use mpich-${MPICH_VER}

    mpienv info mpich-${MPICH_VER} --json >a.json
    assertSuccess python -mjson.tool <a.json >/dev/null
    rm -f a.json

    # Currently mpich is active
    assertEquals "False" "$(mpienv info --json | json_get "broken")"
    assertEquals "MPICH" "$(mpienv info --json | json_get "type")"
    assertEquals ${MPICH_VER} $(mpienv info --json | json_get "version")
    assertTrue $(mpienv info --json | json_check_key "symlink")
    assertTrue $(mpienv info --json | json_check_key "mpiexec")
    assertTrue $(mpienv info --json | json_check_key "mpicc")
    assertTrue $(mpienv info --json | json_check_key "mpicxx")
    assertTrue $(mpienv info --json | json_check_key "default_name")
    assertTrue $(mpienv info --json | json_check_key "prefix")

    assertSuccess test -d $(mpienv prefix)
}

test_mpicc() {
    export TMPDIR=/tmp
    assertSuccess mpienv autodiscover -q --add ${MPI_PREFIX}

    local OUT=$(mktemp)
    local SRC=$(mktemp /tmp/mpienv-test.XXXXXXXX.c)

    cat <<EOF >${SRC}
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <mpi.h>
int main(int argc, char **argv) {
    int size, rank, i;
    int *vals;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    vals = malloc(sizeof(int) * size);
    assert(vals);
    MPI_Gather(&rank, 1, MPI_INT, vals, 1, MPI_INT, 0, MPI_COMM_WORLD);
    if (rank == 0) {
        for(i=0; i<size; i++) {
            printf("%d", vals[i]);
        }
        fflush(stdout);
    }
    free(vals);
    MPI_Finalize();
    return 0;
}
EOF
    # mpienv use ${MPICH}
    # mpicc ${SRC} -o a.out
    # mpiexec -n 2 ./a.out >${OUT}
    # assertEquals "$LINENO: 01" "01" "$(cat $OUT)"
    # mpiexec -n 3 ./a.out >${OUT}
    # assertEquals "$LINENO: 012" "012" "$(cat $OUT)"

    rm -f a.out
    mpienv use ${OMPI}
    mpicc ${SRC} -o a.out
    mpiexec -n 2 --oversubscribe ./a.out >${OUT}
    assertEquals "$LINENO: 01" "01" "$(cat $OUT)"
    mpiexec -n 3 --oversubscribe ./a.out >${OUT}
    assertEquals "$LINENO: 012" "012" "$(cat $OUT)"

    mpienv use ${MPICH}
    mpienv use ${OMPI}
    mpiexec -n 2 -host localhost:2 ./a.out >${OUT}
    assertEquals "$LINENO: 01" "01" "$(cat $OUT)"
    
    rm -f ${SRC} ${OUT} a.out
}

test_mpi4py_clear_pypath() {
    assertSuccess mpienv autodiscover -q --add ${MPI_PREFIX}

    unset PYTHONPATH
    assertNull "${PYTHONPATH:-}"

    mpienv use ${MPICH}
    assertNull "${PYTHONPATH:-}"

    mpienv use --mpi4py ${MPICH}
    assertNotNull "PYTHONPATH must be set for ${MPICH}" "${PYTHONPATH:-}"

    mpienv use ${MPICH}
    assertNull "PYTHONPATH must be NULL" "${PYTHONPATH:-}"

    mpienv use --mpi4py ${MPICH}
    echo "$PYTHONPATH" | grep ${MPICH}
    assertEquals "PYTHONPATH must contain ${MPICH}" 0 $?

    mpienv rename "${MPICH}" mpix
    mpienv use mpix
    assertNull "PYTHONPATH must be NULL" "${PYTHONPATH:-}"

    mpienv use --mpi4py mpix
    echo "$PYTHONPATH" | grep mpix
    assertEquals "PYTHONPATH must contain mpix" 0 $?
}

test_mpi4py() {
    export TMPDIR=/tmp
    assertSuccess mpienv autodiscover -q --add ${MPI_PREFIX}

    local OUT=$(mktemp)
    local SCRIPT=$(mktemp)
    cat <<EOF >$SCRIPT
from mpi4py import MPI
import sys
#print(MPI.__file__)
comm = MPI.COMM_WORLD
rank = comm.Get_rank()


ans = comm.gather(rank, root=0)

if rank == 0:
    print(''.join([str(s) for s in ans]))
EOF
    if ! is_ubuntu1404 ; then
        echo "============== ${MPICH} =============="
        # Ubuntu 14.04's mpich seems to be broken somehow.
        mpienv use ${MPICH}
        mpienv use --mpi4py ${MPICH}
        mpienv exec -host localhost:2 -n 2 $PYTHON -c "from mpi4py import MPI"
        assertTrue "$LINENO: import mpi4py should success" $?

        mpienv exec -host localhost:2 -n 2 $PYTHON $SCRIPT >$OUT
        assertTrue "$LINENO: success" "$?"
        assertEquals "$LINENO: 01" "01" "$(cat $OUT)"

        mpienv exec -host localhost:2 -n 3 $PYTHON $SCRIPT >$OUT
        assertTrue "$LINENO: success" "$?"
        assertEquals "$LINENO: 012" "012" "$(cat $OUT)"
    fi

    echo "============== ${OMPI} =============="
    # test Open MPI
    mpienv use --mpi4py ${OMPI}

    echo PYTHONPATH=$PYTHONPATH

    mpienv exec --oversubscribe -n 2 $PYTHON -c "from mpi4py import MPI"
    which mpiexec
    $PYTHON -c "from mpi4py import MPI; print(MPI.__file__)"
    assertTrue "$LINENO: importing mpi4py from ${OMPI}" "$?"

    mpiexec --oversubscribe -n 2 $PYTHON $SCRIPT
    mpiexec --oversubscribe -n 2 $PYTHON $SCRIPT >$OUT
    # mpienv exec --oversubscribe -n 2 $PYTHON $SCRIPT
    # mpienv exec --oversubscribe -n 2 $PYTHON $SCRIPT >$OUT
    assertEquals "$LINENO: Gather(NP=2) for ${OMPI}" "01" "$(cat $OUT)"

    mpienv exec --oversubscribe -n 4 $PYTHON $SCRIPT >$OUT
    assertEquals "$LINENO: Gather(NP=4) for ${OMPI}" "0123" "$(cat $OUT)"

    rm -f ${SCRIPT}
    rm -f ${OUT}
}


test_reg_issue10(){
    # Regression test for #10
    # https://github.com/keisukefukuda/mpienv/issues/10
    assertSuccess mpienv autodiscover -q --add ${MPI_PREFIX}

    mpienv use --mpi4py ${MPICH} # this command should install mpi4py to mpich-3.2
    mpienv rename ${MPICH} mpix # The mpi4py module should be taken over to 'mpix'

    OUT=$(mpienv use --mpi4py mpix 2>&1) # this command should NOT intall mpi4py again

    # If the `use` command does not run `pip install mpi4py`,
    # which is a correct behavior, E-S should be < 1 [s].
    assertEquals "\$OUT must be empty" "" "${OUT}"
}

# suite() {
#     suite_addTest "test_mpi4py"
#     # suite_addTest "test_mpicc"
# }


#-----------------------------------------------------------
# call shunit2
cd ${old_wd}

SHUNIT2=$(find ${test_dir} -name "shunit2" -type f -path "*2.1*")
echo SHUNIT2="${SHUNIT2}"
#. ${test_dir}/shunit2/2.1/src/shunit2
. ${SHUNIT2}
