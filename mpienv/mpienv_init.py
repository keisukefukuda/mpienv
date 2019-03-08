import sys

_template = """
if [ -z "${MPIENV_ROOT:-}" ]; then
    export MPIENV_ROOT="$HOME/.mpienv"
fi
PYTHON=__SYS_EXECUTABLE__

if [ -z "${MPIENV_VERSIONS_DIR:-}" ]; then
    export MPIENV_VERSIONS_DIR=$MPIENV_ROOT/versions
fi

mkdir -p ${MPIENV_VERSIONS_DIR}

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
                eval "$(env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} $PYTHON -m mpienv.command.use $*)"  # NOQA
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
        "restore" )
            {
                eval "$(env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} $PYTHON -m mpienv.command.restore $*)"  # NOQA
                if [ -z "${BASH_VERSION:-}" -a ! -z "${ZSH_VERSION:-}" ]; then
                    rehash
                fi
            }
            ;;
        "rm" )
            {
                env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                    $PYTHON -m mpienv.command.rm "$@"
            }
            ;;
        "describe" )
            {
                env PYTHONPATH=$MPIENV_ROOT:${PYTHONPATH:-} \
                    $PYTHON -m mpienv.command.describe "$@"
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

mpienv restore
"""


def main():
    print(_template.replace('__SYS_EXECUTABLE__', sys.executable))
