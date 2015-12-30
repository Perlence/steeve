import os

import steeve


def test_no_current(runner, foo_package):
    """Must fail when unstowing a package with no 'current' symlink."""
    result = runner.invoke(steeve.cli, ['unstow', 'foo'])
    assert result.exit_code == 1
    assert 'not stowed' in result.output


def test_unstow(runner, stowed_foo_package):
    """Must remove all previously linked files."""
    result = runner.invoke(steeve.cli, ['unstow', 'foo'])
    assert result.exit_code == 0
    assert not os.path.exists(os.path.join('bin', 'foo'))


def test_strict(runner):
    """Must fail when trying to unstow nonstowed package."""
    result = runner.invoke(steeve.cli, ['unstow', 'nonstowed'])
    assert result.exit_code == 1
    assert 'not stowed' in result.output


def test_unstow_multiple(runner, stowed_foo_package, stowed_bar_package):
    """Must remove previously linked files from multiple packages."""
    result = runner.invoke(steeve.cli, ['unstow', 'foo', 'bar'])
    assert result.exit_code == 0
    assert not os.path.exists(os.path.join('bin', 'foo'))
    assert not os.path.exists(os.path.join('bin', 'bar'))
