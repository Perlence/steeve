import os

import steeve


def test_install_nonexistent(runner):
    """Must fail when trying to install from nonexisting path."""
    result = runner.invoke(steeve.cli, ['install', 'nonexistent', '1.0',
                                        'nonexistent-1.0'])
    assert result.exit_code == 2
    assert 'does not exist' in result.output


def test_install_over_existing(runner, foo_package, foo_updated_release):
    """Must ask for prompt before installing over existing package."""
    assert not os.path.exists(os.path.join('bin', 'foo-1.0'))

    result = runner.invoke(steeve.cli,
                           ['install', 'foo', '1.0', 'releases/foo-1.0'],
                           input='y\n')
    assert result.exit_code == 0
    assert os.path.exists(os.path.join('bin', 'foo-1.0'))
