import os

import steeve


def test_unstow(runner, foo_package):
    """Must remove all previously linked files"""
    result = runner.invoke(steeve.cli, ['stow', 'foo', '1.0'])
    assert result.exit_code == 0

    result = runner.invoke(steeve.cli, ['unstow', 'foo'])
    assert result.exit_code == 0
    assert not os.path.exists(os.path.join('bin', 'foo'))


def test_strict(runner):
    """Must fail when trying to unstow nonstowed package"""
    result = runner.invoke(steeve.cli, ['unstow', 'nonstowed'])
    assert result.exit_code == 1
    assert 'not stowed' in result.output
