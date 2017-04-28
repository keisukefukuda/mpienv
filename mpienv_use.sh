set -ue
declare -r ROOT=$HOME/.mpienv

mpi=$1

new_ldpath=$(python ${ROOT}/update_lib.py ${ROOT} "$LD_LIBRARY_PATH" "$mpi")
if [ "$?" != 0 ]; then
    return
fi

new_path=$(python ${ROOT}/update_path.py ${ROOT} "$PATH" "$mpi")
if [ "$?" != 0 ]; then
    return
fi

echo export LD_LIBRARY_PATH=$new_ldpath
echo export PATH=$new_path
