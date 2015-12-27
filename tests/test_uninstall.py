import os

import steeve


def test_interrupt_uninstall(runner, foo_package):
    """Must not uninstall unless user inputs 'y'."""
    result = runner.invoke(steeve.cli, ['uninstall', 'foo', '1.0'],
                           input='n\n')
    assert result.exit_code == 1
    assert os.path.exists(os.path.join('stow', 'foo', '1.0'))


def test_uninstall_unstowed_version(runner, foo_package):
    """Must remove the whole package if version is single."""
    result = runner.invoke(steeve.cli, ['uninstall', 'foo', '1.0'],
                           input='y\n')
    assert result.exit_code == 0
    assert not os.path.exists(os.path.join('stow', 'foo', '1.0'))
    assert not os.path.exists(os.path.join('stow', 'foo'))


def test_uninstall_stowed_version(runner, stowed_foo_package):
    """Must unstow and remove the whole package if version is single."""
    assert os.path.exists(os.path.join('bin', 'foo'))

    result = runner.invoke(steeve.cli, ['uninstall', 'foo', '1.0'],
                           input='y\n')
    assert result.exit_code == 0
    assert not os.path.exists(os.path.join('bin', 'foo'))
    assert not os.path.exists(os.path.join('stow', 'foo', '1.0'))
    assert not os.path.exists(os.path.join('stow', 'foo'))


def test_uninstall_stowed_multiversion(runner, stowed_bar_package):
    """Must unstow and remove only given version."""
    assert os.path.exists(os.path.join('bin', 'bar'))

    result = runner.invoke(steeve.cli, ['uninstall', 'bar', '1.0'],
                           input='y\n')
    assert result.exit_code == 0
    assert not os.path.exists(os.path.join('bin', 'bar'))
    assert not os.path.exists(os.path.join('stow', 'bar', '1.0'))
    assert os.path.exists(os.path.join('stow', 'bar', '2.0'))


def test_uninstall_unstowed_package(runner, foo_package):
    """Must remove the whole package."""
    result = runner.invoke(steeve.cli, ['uninstall', 'foo'],
                           input='y\n')
    assert result.exit_code == 0
    assert not os.path.exists(os.path.join('stow', 'foo'))


def test_uninstall_unstowed_package_with_two_versions(runner, bar_package):
    """Must remove the whole package."""
    result = runner.invoke(steeve.cli, ['uninstall', 'bar'],
                           input='y\n')
    assert result.exit_code == 0
    assert not os.path.exists(os.path.join('stow', 'bar'))


def test_uninstall_stowed_package(runner, stowed_bar_package):
    """Must unstow and remove the whole package."""
    assert os.path.exists(os.path.join('bin', 'bar'))

    result = runner.invoke(steeve.cli, ['uninstall', 'bar'],
                           input='y\n')
    assert result.exit_code == 0
    assert not os.path.exists(os.path.join('bin', 'bar'))
    assert not os.path.exists(os.path.join('stow', 'bar'))
