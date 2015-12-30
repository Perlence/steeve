import os

import pytest
from click.testing import CliRunner

import steeve


@pytest.yield_fixture
def runner():
    runner = CliRunner()
    with runner.isolated_filesystem() as target:
        dir = os.path.join(target, 'stow')
        os.makedirs(dir)
        runner.env['STEEVE_DIR'] = dir
        runner.env['STEEVE_TARGET'] = target
        yield runner


@pytest.fixture
def foo_package():
    """Return a package with single version."""
    binpath = os.path.join('stow', 'foo', '1.0', 'bin')
    os.makedirs(binpath)
    with open(os.path.join(binpath, 'foo'), 'w'):
        pass
    return 'foo'


@pytest.fixture
def stowed_foo_package(runner, foo_package):
    result = runner.invoke(steeve.cli, ['--no-folding', 'stow', 'foo', '1.0'])
    assert result.exit_code == 0


@pytest.fixture
def foo_release():
    """Return a package with single version."""
    binpath = os.path.join('releases', 'foo-1.0', 'bin')
    os.makedirs(binpath)
    with open(os.path.join(binpath, 'foo'), 'w'):
        pass
    return 'foo'


@pytest.fixture
def foo_updated_release(foo_release):
    """Return a package with updated single version."""
    binpath = os.path.join('releases', 'foo-1.0', 'bin')
    with open(os.path.join(binpath, 'foo-1.0'), 'w'):
        pass
    return 'foo'


@pytest.fixture
def bar_package():
    """Return a package with two versions."""
    for version in ('1.0', '2.0'):
        binpath = os.path.join('stow', 'bar', version, 'bin')
        os.makedirs(binpath)
        with open(os.path.join(binpath, 'bar'), 'w'):
            pass


@pytest.fixture
def stowed_bar_package(runner, bar_package):
    result = runner.invoke(steeve.cli, ['--no-folding', 'stow', 'bar', '1.0'])
    assert result.exit_code == 0
