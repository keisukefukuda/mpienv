set -u

date
hostname

if [ -n "${ZSH_VERSION:-}" ]; then
    setopt shwordsplit
    SHUNIT_PARENT=$0
fi

declare -r test_dir=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
declare -r proj_dir=$(cd ${test_dir}/..; pwd)

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

setUp() {
    rm -rf ${MPIENV_VERSIONS_DIR}
    mkdir -p ${MPIENV_VERSIONS_DIR}
}

tearDown() {
    rm -rf ${MPIENV_VERSIONS_DIR}
}

assertSuccess() {
    ret=0
    $* || ret=$?
    assertTrue "'$*' Success" "$?"
}

# Load mpienv
. ${proj_dir}/init

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

if is_ubuntu1404 ; then
    echo "Running on Ubuntu 14.04"
    export MPICH_VER=3.0.4
    export MPICH_EXEC="/usr/bin/mpiexec.mpich"
    export MPICH_CC_BIN="/usr/bin/mpicc.mpich" # avoid MPICH_CC
    export MPICH_PREF="/usr"

    export OMPI_VER=1.6.5
    export OMPI_EXEC="/usr/bin/mpiexec.openmpi"
    export OMPI_CC_BIN="/usr/bin/mpicc.openmpi"
    export OMPI_PREF="/usr"

    export SYS_PREFIX=/usr

elif is_macos; then
    echo "Running on MacOS"
    export MPICH_VER=3.2
    export MPICH_PREF="/usr/local/Cellar/mpich/3.2_3"
    export MPICH_EXEC="${MPICH_PREF}/bin/mpiexec"
    export MPICH_CC_BIN="${MPICH_PREF}/bin/mpicc"

    export OMPI_VER=2.1.1
    export OMPI_PREF="/usr/local/Cellar/open-mpi/2.1.1"
    export OMPI_EXEC="${OMPI_PREF}/bin/mpiexec"
    export OMPI_CC_BIN="${OMPI_PREF}/bin/mpicc"

    export SYS_PREFIX=/usr/local/Cellar
else
    echo "Unknown test platform: OSTYPE=${OSTYPE}" >&2
    echo "----------------------------"
    if [ -f /etc/lsb-release ]; then
        echo "/etc/lsb-release:"
        cat  /etc/lsb-release
    else
        echo "/etc/lsb-release does not exist."
    fi
    echo "----------------------------"
    exit -1
fi

export MPICH=mpich-${MPICH_VER}
export OMPI=openmpi-${OMPI_VER}

print_mpi_info() {
    unset tmpfile
    local tmpfile=$(mktemp "/tmp/${0##*/}.tmp.XXXXXX")
    local MPIEXEC=$1
    local INFO=$2
    cat <<EOF >${tmpfile}
from mpienv.mpi import MPI
from mpienv import mpienv
cls = MPI(mpienv, '${MPIEXEC}')
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

    flake8 $(find . -name "*.py" | grep -v pylib)
    assertEquals 0 $?
}

test_empty_list() {
    # There should  be nothing in MPIENV_VERSIONS_DIR
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
    assertEquals ${MPICH_PREF} "${PREF}"

    local VER=$(print_mpi_info ${MPICH_EXEC} "version")
    assertEquals ${MPICH_VER} ${VER}
}

test_openmpi_info() {
    local EXEC=$(print_mpi_info ${OMPI_EXEC} "mpiexec")
    assertEquals ${OMPI_EXEC} ${EXEC}

    local CC=$(print_mpi_info ${OMPI_EXEC} "mpicc")
    assertEquals ${OMPI_CC_BIN} ${CC}

    local PREF=$(print_mpi_info ${OMPI_EXEC} "prefix")
    assertEquals ${OMPI_PREF} ${PREF}

    local VER=$(print_mpi_info ${OMPI_EXEC} "version")
    assertEquals ${OMPI_VER} ${VER}
}

test_1mpi() {
    # mpienv list
    mpienv autodiscover -q --add ${SYS_PREFIX}

    mpienv list | grep -q mpich-${MPICH_VER}
    assertTrue "$?"

    # Test json output
    mpienv list --json | python -c "import json;import sys; json.load(sys.stdin)"
    assertTrue "$?"

    # Test rename
    # rename mpich -> my-cool-mpi
    mpienv rename mpich-${MPICH_VER} my-cool-mpi
    assertTrue "$?"
    mpienv list | grep -qE 'my-cool-mpi'
    assertTrue "$?"

    mpienv list | grep -qE mpich-${MPICH_VER}
    assertFalse "$?"

    # Rename back to mpich
    mpienv rename my-cool-mpi mpich-${MPICH_VER}
    mpienv list | grep -q "mpich-${MPICH_VER}"
    assertTrue "$?"

    # Remove mpich
    assertSuccess mpienv use openmpi-${OMPI_VER}  # Activate Open MPI to remove mpich
    assertSuccess mpienv rm mpich-${MPICH_VER}    # Remove mpich
    mpienv list | grep -q mpich-${MPICH_VER} # Check if it's removed
    assertFalse "$?"  # THus the grep should fail
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
    assertSuccess mpienv autodiscover -q --add ${SYS_PREFIX}
    mpienv use mpich-${MPICH_VER}

    mpienv info mpich-${MPICH_VER} --json >a.json
    mpienv info --json >b.json

    assertSuccess diff -q a.json b.json

    rm -f a.json b.json

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
    assertSuccess mpienv autodiscover -q --add ${SYS_PREFIX}

    local OUT=$(mktemp)
    local SRC=$(mktemp /tmp/mpienv-test.XXXXXXXX.c)

    cat <<EOF >${SRC}
#include <stdio.h>
#include <mpi.h>
int main(int argc, char **argv) {
    int size, rank, i;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    for (i=0; i < size; i++) {
        if (i == rank) {
            printf("%d", i);
            fflush(stdout);
        }
        MPI_Barrier(MPI_COMM_WORLD);
    }
    MPI_Finalize();
    return 0;
}
EOF
    mpienv use ${MPICH}
    mpicc ${SRC} -o a.out
    mpiexec -n 2 ./a.out >${OUT}
    assertEquals "$LINENO: 01" "01" "$(cat $OUT)"
    mpiexec -n 3 ./a.out >${OUT}
    assertEquals "$LINENO: 012" "012" "$(cat $OUT)"

    rm -f a.out
    mpienv use ${OMPI}
    mpicc ${SRC} -o a.out
    mpiexec -n 2 ./a.out >${OUT}
    assertEquals "$LINENO: 01" "01" "$(cat $OUT)"
    mpiexec -n 3 ./a.out >${OUT}
    assertEquals "$LINENO: 012" "012" "$(cat $OUT)"

    mpienv use ${MPICH}
    mpienv use ${OMPI}
    mpiexec -n 2 ./a.out >${OUT}
    assertEquals "$LINENO: 01" "01" "$(cat $OUT)"
    
    rm -f ${SRC} ${OUT} a.out
}

test_mpi4py() {
    assertSuccess mpienv autodiscover -q --add ${SYS_PREFIX}
    export TMPDIR=/tmp

    local OUT=$(mktemp)
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
    mpienv use ${MPICH}
    mpienv use --mpi4py ${MPICH}
    mpienv exec -n 2 python -c "from mpi4py import MPI"
    assertTrue "$LINENO: import mpi4py should success" $?
    
    mpienv exec -n 2 python $SCRIPT >$OUT
    assertTrue "$LINENO: success" "$?"
    assertEquals "$LINENO: 01" "01" "$(cat $OUT)"
    
    mpienv exec -n 3 python $SCRIPT >$OUT
    assertTrue "$LINENO: success" "$?"
    assertEquals "$LINENO: 012" "012" "$(cat $OUT)"

    # test Open MPI
    mpienv use --mpi4py ${OMPI}
    mpienv exec -n 2 python -c "from mpi4py import MPI"
    assertTrue "$LINENO: command success" "$?"

    mpienv exec -n 2 python $SCRIPT >$OUT
    assertEquals "01" "$(cat $OUT)"

    mpienv exec -n 4 python $SCRIPT >$OUT
    assertEquals "0123" "$(cat $OUT)"

    rm -f ${SCRIPT}
    rm -f ${OUT}
}

test_mpi4py_clear_pypath() {
    assertSuccess mpienv autodiscover -q --add ${SYS_PREFIX}

    unset PYTHONPATH
    assertNull "${PYTHONPATH:-}"

    mpienv use ${MPICH}
    assertNull "${PYTHONPATH:-}"

    mpienv use --mpi4py ${MPICH}
    assertNotNull "${PYTHONPATH:-}"

    mpienv use ${MPICH}
    assertNull "${PYTHONPATH:-}"
}

test_reg_issue10(){
    # Regression test for #10
    # https://github.com/keisukefukuda/mpienv/issues/10
    assertSuccess mpienv autodiscover -q --add ${SYS_PREFIX}

    mpienv use --mpi4py ${MPICH} # this command should install mpi4py to mpich-3.2
    mpienv rename ${MPICH} mpix # The mpi4py module should be taken over to 'mpix'

    OUT=$(mpienv use --mpi4py mpix 2>&1) # this command should NOT intall mpi4py again

    # If the `use` command does not run `pip install mpi4py`,
    # which is a correct behavior, E-S should be < 1 [s].
    assertEquals "\$OUT must be empty" "" "${OUT}"
}

# suite() {
#     suite_addTest "test_mpi4py"
#     suite_addTest "test_mpicc"
# }


#-----------------------------------------------------------
# call shunit2
cd ${old_wd}

. ${test_dir}/shunit2/source/2.1/src/shunit2
