import steeve


def test_no_stow(runner):
    """Test steeve does not do anything unless GNU stow is installed"""
    # Clean PATH so 'stow' won't be found
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
