import steeve


def test_no_stow(runner, foo_release, foo_package):
    """Must not do anything unless GNU stow is installed."""
    # Clean PATH so 'stow' won't be found
    runner.env['PATH'] = ''
    require_stow = [
        ['install', 'foo', '1.0', 'releases/foo-1.0'],
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


def test_valid_version(runner):
    """Must fail when given version is 'current'."""
    result = runner.invoke(steeve.cli, ['stow', 'foo', 'current'])
    assert result.exit_code == 2
    assert "must not be 'current'" in result.output
