import os

import pytest
from click.testing import CliRunner


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
