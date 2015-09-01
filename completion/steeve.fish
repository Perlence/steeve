function __fish_steeve_no_subcommand -d 'Test if steeve has yet to be given a subcommand'
    for i in (commandline -opc)
        if contains -- $i install ls reinstall restow stow uninstall unstow
            return 1
        end
    end
    return 0
end

function __fish_steeve_packages -d 'List steeve packages'
    set dir /usr/local/stow
    if [ -n "$STEEVE_DIR" ]
        set dir $STEEVE_DIR
    end

    ls $dir
    set -e dir
end

function __fish_steeve_versions -d 'List package versions'
    set -l cmd (commandline -opc)
    set -l package $cmd[-1]

    set dir /usr/local/stow
    if [ -n "$STEEVE_DIR" ]
        set dir $STEEVE_DIR
    end

    for p in (ls $dir/$package)
        if [ "$p" != "current" ]
            echo $p
        end
    end
    set -e dir
end

function __fish_steeve_await_package -a subcommand -d 'Test if steeve has yet to be given a package name'
    set -l cmd (commandline -opc)
    if [ $cmd[-1] = $subcommand ]
        return 0
    end
    return 1
end

function __fish_steeve_await_version -a subcommand -d 'Test if steeve has yet to be given a version'
    set -l cmd (commandline -opc)
    if [ (count $cmd) -lt 3 ]
        return 1
    end
    if [ $cmd[-2] = $subcommand ]
        return 0
    end
    return 1
end

complete -c steeve -f -n '__fish_steeve_no_subcommand' -s d -l dir        -d 'Set location of packages to DIR'
complete -c steeve -f -n '__fish_steeve_no_subcommand' -s t -l target     -d 'Set stow target to DIR'
complete -c steeve -f -n '__fish_steeve_no_subcommand'      -l no-folding -d 'Disable folding of newly stowed directories'
complete -c steeve -f -n '__fish_steeve_no_subcommand' -s v -l verbose    -d 'Increase verbosit'
complete -c steeve -f -n '__fish_steeve_no_subcommand'      -l help       -d 'Show help message and exit'

complete -c steeve    -f -n '__fish_steeve_no_subcommand'           -a install                    -d 'Install package from given folder'
complete -c steeve -A -f -n '__fish_steeve_await_package install'   -a '(__fish_steeve_packages)' -d 'Package'
complete -c steeve -A -f -n '__fish_steeve_await_version install'   -a '(__fish_steeve_versions)' -d 'Version'

complete -c steeve    -f -n '__fish_steeve_no_subcommand'           -a ls                         -d 'List packages or package versions'
complete -c steeve -A -f -n '__fish_steeve_await_package ls'        -a '(__fish_steeve_packages)' -d 'Package'

complete -c steeve    -f -n '__fish_steeve_no_subcommand'           -a reinstall                  -d 'Reinstall package from given folder'
complete -c steeve -A -f -n '__fish_steeve_await_package reinstall' -a '(__fish_steeve_packages)' -d 'Package'
complete -c steeve -A -f -n '__fish_steeve_await_version reinstall' -a '(__fish_steeve_versions)' -d 'Version'

complete -c steeve    -f -n '__fish_steeve_no_subcommand'           -a restow                     -d 'Restow (like unstow followed by stow)'
complete -c steeve -A -f -n '__fish_steeve_await_package restow'    -a '(__fish_steeve_packages)' -d 'Package'
complete -c steeve -A -f -n '__fish_steeve_await_version restow'    -a '(__fish_steeve_versions)' -d 'Version'

complete -c steeve    -f -n '__fish_steeve_no_subcommand'           -a stow                       -d 'Stow given package version into target dir'
complete -c steeve -A -f -n '__fish_steeve_await_package stow'      -a '(__fish_steeve_packages)' -d 'Package'
complete -c steeve -A -f -n '__fish_steeve_await_version stow'      -a '(__fish_steeve_versions)' -d 'Version'

complete -c steeve    -f -n '__fish_steeve_no_subcommand'           -a uninstall                  -d 'Remove the whole package or specific version'
complete -c steeve -A -f -n '__fish_steeve_await_package uninstall' -a '(__fish_steeve_packages)' -d 'Package'
complete -c steeve -A -f -n '__fish_steeve_await_version uninstall' -a '(__fish_steeve_versions)' -d 'Version'

complete -c steeve    -f -n '__fish_steeve_no_subcommand'           -a unstow                     -d 'Delete stowed symlinks'
complete -c steeve -A -f -n '__fish_steeve_await_package unstow'    -a '(__fish_steeve_packages)' -d 'Package'
