import sys

_template = """
export MPIENV_ROOT="$HOME/.mpienv"
PYTHON=__SYS_EXECUTABLE__

if [ -z "${MPIENV_VERSIONS_DIR:-}" ]; then
    export MPIENV_VERSIONS_DIR=$MPIENV_ROOT/versions
fi

mkdir -p ${MPIENV_VERSIONS_DIR}
mkdir -p ${MPIENV_VERSIONS_DIR}/shims

if [ ! -f $MPIENV_VERSIONS_DIR/shims ]; then
    G=$MPIENV_VERSIONS_DIR/version_global
    if [ -f $G ]; then
        ln -s $(cat $G) $MPIENV_VERSIONS_DIR/shims
    fi
fi

export PATH=$MPIENV_VERSIONS_DIR/shims/bin:${PATH:-}
export LD_LIBRARY_PATH=${MPIENV_VERSIONS_DIR}/shims/lib:${MPIENV_VERSIONS_DIR}/shims/lib64:${LD_LIBRARY_PATH:-}  # NOQA

function usage() {
    echo "Usage: mpienv [command] [options...]"
}

function mpienv() {
    if [ "0" = "${#*}" ]; then
        usage
        return -1
    fi

    declare -r root=$MPIENV_ROOT
    declare -r command="$1"
    shift

    case "$command" in
        "use" )
            {
                eval $(env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                           $PYTHON -m mpienv.command.use $*)
                if [ -z "${BASH_VERSION:-}" -a ! -z "${ZSH_VERSION:-}" ]; then
                    rehash
                fi
            }
            ;;
        "add" )
            {
               env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                   $PYTHON -m mpienv.command.add $*
            }
            ;;
        "rm" )
            {
                env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                    $PYTHON -m mpienv.command.rm "$@"
            }
            ;;
        "rename" )
            {
                env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                    $PYTHON -m mpienv.command.rename "$@"
            }
            ;;
        "list" )
            {
                env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                    $PYTHON -m mpienv.command.list "$@"
            }
            ;;
        "info" )
            {
                env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                    $PYTHON -m mpienv.command.info "$@"
            }
            ;;
        "autodiscover" )
            {
                env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                    $PYTHON -m mpienv.command.autodiscover "$@"
            }
            ;;
        "prefix" )
            {
                env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                    $PYTHON -m mpienv.command.prefix "$@"
            }
            ;;
        "exec" )
            {
                env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                    $PYTHON -m mpienv.command.exec "$@"
            }
            ;;
        "help" )
            {
                env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                    $PYTHON -m mpienv.command.help "$@"
            }
            ;;
        * )
            echo "mpienv [ERROR]: Unknown command '$command'"
            ;;
    esac
}
"""


def main():
    print(_template.replace('__SYS_EXECUTABLE__', sys.executable))
