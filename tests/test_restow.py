import os

import steeve


def test_restow(runner, foo_package):
    """Must stow new files that were added after initial stow"""
    result = runner.invoke(steeve.cli, ['stow', 'foo', '1.0'])
    assert result.exit_code == 0
    assert not os.path.exists(os.path.join('bin', 'bar'))

    # Create a new file
    with open(os.path.join('stow', 'foo', '1.0', 'bin', 'bar'), 'w'):
        pass

    result = runner.invoke(steeve.cli, ['restow', 'foo'])
    assert result.exit_code == 0
    assert os.path.exists(os.path.join('bin', 'bar'))
