set -g subcommands install ls reinstall restow stow uninstall unstow

function __steeve_seq -a upto
    seq 1 1 $upto ^ /dev/null
end


function __steeve_no_subcommand -d 'Test if steeve has yet to be given a subcommand'
    for i in (commandline -opc)
        if contains -- $i $subcommands
            return 1
        end
    end
    return 0
end

function __steeve_without_subcommand -d 'Strip all words starting from subcommand'
    set -l cmd (commandline -opc)
    for i in (seq (count $cmd))
        if contains -- $cmd[$i] $subcommands
            set steeve_without_subcommand $cmd[1..(math $i - 1)]
            break
        end
    end
    if test -z "$steeve_without_subcommand"
        set steeve_without_subcommand $cmd
    end

    eval "$steeve_without_subcommand $argv 2>/dev/null"
    set -e steeve_without_subcommand
end

function __steeve_packages -d 'List steeve packages'
    __steeve_without_subcommand ls -q
end

function __steeve_versions -d 'List package versions'
    set -l cmd (commandline -opc)
    set -l package $cmd[-1]
    __steeve_without_subcommand ls -q $package
end

function __steeve_await_package -a subcommand -d 'Test if steeve has yet to be given a package name'
    set -l cmd (commandline -opc)
    test $cmd[-1] = $subcommand
end

function __steeve_await_version -a subcommand -d 'Test if steeve has yet to be given a version'
    set -l cmd (commandline -opc)
    test (count $cmd) -gt 2; and test $cmd[-2] = $subcommand
end

complete -c steeve -f -n '__steeve_no_subcommand' -s d -l dir        -d 'Set location of packages to DIR'
complete -c steeve -f -n '__steeve_no_subcommand' -s t -l target     -d 'Set stow target to DIR'
complete -c steeve -f -n '__steeve_no_subcommand'      -l no-folding -d 'Disable folding of newly stowed directories'
complete -c steeve -f -n '__steeve_no_subcommand' -s v -l verbose    -d 'Increase verbosity'
complete -c steeve -f -n '__steeve_no_subcommand'      -l help       -d 'Show help message and exit'

complete -c steeve    -f -n '__steeve_no_subcommand'             -a install               -d 'Install package from given folder'
complete -c steeve -A -f -n '__steeve_await_package install'     -a '(__steeve_packages)' -d 'Package'
complete -c steeve -A -f -n '__steeve_await_version install'     -a '(__steeve_versions)' -d 'Version'

complete -c steeve    -f -n '__steeve_no_subcommand'             -a ls                    -d 'List packages or package versions'
complete -c steeve -A -f -n '__fish_seen_subcommand_from ls'     -a '(__steeve_packages)' -d 'Package'
complete -c steeve    -f -n '__fish_seen_subcommand_from ls'     -s q -l quiet            -d 'Display packages or versions without formatting'

complete -c steeve    -f -n '__steeve_no_subcommand'             -a stow                  -d 'Stow given package version into target dir'
complete -c steeve -A -f -n '__steeve_await_package stow'        -a '(__steeve_packages)' -d 'Package'
complete -c steeve -A -f -n '__steeve_await_version stow'        -a '(__steeve_versions)' -d 'Version'

complete -c steeve    -f -n '__steeve_no_subcommand'             -a uninstall             -d 'Remove the whole package or specific version'
complete -c steeve -A -f -n '__steeve_await_package uninstall'   -a '(__steeve_packages)' -d 'Package'
complete -c steeve -A -f -n '__steeve_await_version uninstall'   -a '(__steeve_versions)' -d 'Version'

complete -c steeve    -f -n '__steeve_no_subcommand'             -a unstow                -d 'Delete stowed symlinks'
complete -c steeve -A -f -n '__fish_seen_subcommand_from unstow' -a '(__steeve_packages)' -d 'Package'
