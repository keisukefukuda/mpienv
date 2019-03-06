from mpienv.util import escape_shell_commands


def test_escape_shell_commands():
    inp = ['python', 'train_mnist.py', '-g']
    ans = inp  # no change
    assert ans == escape_shell_commands(inp)

    inp = ['python', 'train_mnist.py', 'param with space']
    ans = ['python', 'train_mnist.py', '"param with space"']
    assert ans == escape_shell_commands(inp)

    inp = ['python', 'train_mnist.py', 'param with "']
    ans = ['python', 'train_mnist.py', '"param with \\""']
    assert ans == escape_shell_commands(inp)

    inp = ['python', 'train_mnist.py', 'param with \'']
    ans = ['python', 'train_mnist.py', '"param with \'"']
    assert ans == escape_shell_commands(inp)

    inp = ['some special chars *']
    ans = ['"some special chars *"']
    assert ans == escape_shell_commands(inp)


