import os

import pytest
from click.testing import CliRunner

import steeve


@pytest.yield_fixture
def runner(scope='function'):
    runner = CliRunner()
    with runner.isolated_filesystem() as target:
        dir = os.path.join(target, 'stow')
        os.makedirs(dir)
        runner.env['STEEVE_DIR'] = dir
        runner.env['STEEVE_TARGET'] = target
        yield runner


@pytest.fixture
def foo_package():
    binpath = os.path.join('stow', 'foo', '1.0', 'bin')
    os.makedirs(binpath)
    with open(os.path.join(binpath, 'foo'), 'w'):
        pass
    return 'foo'


def test_no_stow(runner):
    """Test steeve does not do anything unless GNU stow is installed"""
    runner.env['PATH'] = ''
    require_stow = [
        ['install', 'foo', '1.0', 'releases/foo-1.0'],
        ['reinstall', 'foo', '1.0', 'releases/foo-1.0'],
        ['uninstall', 'foo', '1.0'],
        ['stow', 'foo', '1.0'],
        ['unstow', 'foo'],
        ['restow', 'foo'],
    ]
    for args in require_stow:
        result = runner.invoke(steeve.cli, args)
        assert result.exit_code == 1
        assert 'GNU Stow is not installed' in result.output

    result = runner.invoke(steeve.cli, ['ls'])
    assert result.exit_code == 0
    assert 'GNU Stow is not installed' not in result.output
