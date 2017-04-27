
function mpienv() {
    cmd=$1

    if [ "$cmd" = "use" ]; then
        mpi="${2:-}"
        if [ -z "$mpi" ]; then
            echo "Usage: mpienv use [mpi]" >&2
        fi
        mpienv_use "$mpi"
    else
        echo "Unknown command '$cmd'" >&2
        return
    fi
}

function mpienv_use() {
    mpi=$1
    local -r dir_name=$HOME/.mpienv
    
    new_ldpath=$(python $dir_name/update_lib.py $dir_name "$LD_LIBRARY_PATH" "$mpi")
    if [ "$?" != 0 ]; then
        return
    fi

    new_path=$(python $dir_name/update_path.py $dir_name "$PATH" "$mpi")
    if [ "$?" != 0 ]; then
        return
    fi

    echo export LD_LIBRARY_PATH=$new_ldpath
    echo export PATH=$new_path
}

