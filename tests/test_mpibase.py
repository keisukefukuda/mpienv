import tempfile
import os

from mpienv.mpibase import parse_hosts
from mpienv.mpibase import split_mpi_user_prog


_test_hostfile = """
host1: slots=1
host2
host2
host3: slots=2  # This is a comment
localhost

"""

def test_parse_hosts():
    temp = tempfile.NamedTemporaryFile(delete=False)
    try:
        temp.write(_test_hostfile.encode('utf-8'))
        temp.close()

        for opt in ['--hostfile', '-hostfile', '--machinefile', '-machinefile']:
            result = parse_hosts([opt, temp.name])
            assert result == ['host1', 'host2', 'host3', 'localhost']

    finally:
        os.remove(temp.name)

    assert ['localhost'] == parse_hosts([])
    assert ['localhost'] == parse_hosts(['some', 'extra', 'options'])

    for opt in ['-H', '-host', '--host']:
        assert ['host1'] == parse_hosts([opt, 'host1']), 'test {}'.format(opt)

    for opt in ['-H', '-host', '--host']:
        assert ['host1', 'host2'] == parse_hosts([opt, 'host1,host2'])
        assert ['host1', 'host2'] == parse_hosts([opt, 'host2,host1'])
        assert ['host1'] == parse_hosts([opt, 'host1,host1'])


def test_split_mpi_user_prog():
    cmd = ['-n', '2', 'ls', '-l']
    mpi = ['-n', '2']
    usr = ['ls', '-l']
    ans = (mpi, usr)
    assert ans == split_mpi_user_prog(cmd)

    cmd = ['ls', '-l']
    mpi = []
    usr = ['ls', '-l']
    ans = (mpi, usr)
    assert ans == split_mpi_user_prog(cmd)

    cmd = ['-n', '2', '--hostfile', 'hostfile', '--mca', 'btl', 'openib',
           '--map-by', 'ppr:2:node', 'python', 'train_mnist.py', '-g']
    mpi = ['-n', '2', '--hostfile', 'hostfile', '--mca', 'btl', 'openib',
           '--map-by', 'ppr:2:node']
    usr = ['python', 'train_mnist.py', '-g']
    ans = (mpi, usr)
    assert ans == split_mpi_user_prog(cmd)
