import os

import steeve


def test_nonexistent(runner, foo_package):
    """Must fail when trying to stow nonexistent package."""
    result = runner.invoke(steeve.cli, ['stow', 'nonexistent', '0.0'])
    assert result.exit_code == 1
    assert 'not installed' in result.output


def test_folding(runner, foo_package):
    """Must link the whole 'bin' folder."""
    result = runner.invoke(steeve.cli, ['stow', 'foo', '1.0'])
    assert result.exit_code == 0
    assert os.path.islink('bin')
    assert not os.path.islink(os.path.join('bin', 'foo'))


def test_no_folding(runner, foo_package):
    """Must create all missing folders."""
    result = runner.invoke(steeve.cli, ['--no-folding', 'stow', 'foo', '1.0'])
    assert result.exit_code == 0
    assert not os.path.islink('bin')
    assert os.path.islink(os.path.join('bin', 'foo'))


def test_clean_up(runner, foo_package):
    """Must remove 'current' link when stow failed."""
    # Make target dirty
    os.mkdir('bin')
    with open(os.path.join('bin', 'foo'), 'w'):
        pass

    result = runner.invoke(steeve.cli, ['stow', 'foo', '1.0'])
    assert result.exit_code == 1
    assert not os.path.exists(os.path.join('stow', 'foo', 'current'))
