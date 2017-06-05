set -eu

declare -r test_dir=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
declare -r proj_dir=$(cd ${test_dir}/..; pwd)

old_wd=$PWD

echo "proj_dir=$proj_dir"

cd ${test_dir}

if [ ! -d "${test_dir}/shunit2" ] ; then
    git clone https://github.com/kward/shunit2.git
fi


test_empty_list() {
    TMPDIR=$(mktemp -d)
    
    rm -rf ${TMPDIR}
}

#-----------------------------------------------------------
# call shunit2
cd ${old_wd}
. ${test_dir}/shunit2/source/2.1/src/shunit2
