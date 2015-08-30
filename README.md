# steeve

Tiny [GNU Stow](https://www.gnu.org/software/stow/)–based package manager.


## Summary

*steeve* is not a replacement for any full-fledged package manager like *dpkg* or *yum*, but instead an addition, designed to handle manually built software and binary distributions. Instead of polluting `/usr/local` with binaries and libraries that aren't tracked by any package manager and thus cannot be safely removed or upgraded, *steeve* provides a structured approach that allows for managing multiple software versions in a matter of a command.


## Packages

By default packages live in `/usr/local/stow`. This location is configured either via environment variable `STEEVE_DIR` or command-line option `-d`, `--dir`. A package consists of one or multiple subdirectories named after version. Each version has directories with files that will be linked into *target directory*, which is `/usr/local` by default. Target directory can be changed via environment variable `STEEVE_TARGET` or command-line option `-t`, `--target`. The prominent part of a package is symbolic link named `current` that points to current version.

Here's an example of a valid package tree:

```bash
$ tree /usr/local/stow/tig
/usr/local/stow/tig
├── 2.1
│   ├── bin
│   │   └── tig
│   └── etc
│       └── tigrc
├── 2.1.1
│   ├── bin
│   │   └── tig
│   └── etc
│       └── tigrc
└── current -> /usr/local/stow/tig/2.1.1

7 directories, 4 files
```


## Tree Folding

The main gotcha is GNU Stow's tree folding mechanism. Please, get accustomed to it by reading chapter [Installing Packages](http://www.gnu.org/software/stow/manual/stow.html#Installing-Packages) of GNU Stow manual. You can disable folding by setting environment variable `STEEVE_NO_FOLDING` or passing `--no-folding` option.


## Dependencies

- Python 2.7
- GNU Stow 2.2


## Installation

1.  Clone the repository:

    ```bash
    $ git clone https://github.com/Perlence/steeve.git
    ```

2.  Install the package:

    ```bash
    $ pip install .
    ```


## Usage

Run *steeve* with `--help` option to see the list of commands:

```bash
$ steeve --help
```

To see usage of a command, run:

```bash
$ steeve COMMAND --help
```

*steeve* helps you install manually built programs. For example, to install [tig](http://jonas.nitro.dk/tig/), text-mode interface for git, first download the release tarball:

```bash
$ curl -O -L http://jonas.nitro.dk/tig/releases/tig-2.1.1.tar.gz
```

Then configure, make and install with prefix:

```bash
$ ./configure
$ make prefix=/usr/local
$ sudo make install prefix=/usr/local/stow/tig/2.1.1
```

Finally, stow tig 2.1.1 into `/usr/local` with *steeve*:

```bash
$ sudo steeve use tig 2.1.1
```

Under the covers `steeve use` creates a symbolic link to current version and runs `stow` to link contents of `current` into `/usr/local`:

```bash
$ sudo ln -s /usr/local/stow/tig/2.1.1 /usr/local/stow/tig/current
$ sudo stow -t /usr/local -d tig current
```

Also *steeve* can manage binary distributions. For instance, let's install Node.js binaries:

```bash
$ curl -O -L https://nodejs.org/dist/v0.12.7/node-v0.12.7-linux-x64.tar.gz
$ tar xf node-v0.12.7-linux-x64.tar.gz
$ cd node-v0.12.7-linux-x64
$ ls
bin/  ChangeLog  include/  lib/  LICENSE  README.md  share/
```

There are some text files that don't belong to `/usr/local`, so remove them:

```bash
$ rm ChangeLog LICENSE README.md
$ cd ..
```

Now, install Node.js from directory with `steeve install`:

```bash
$ sudo steeve install node 0.12.7 ./node-v0.12.7-linux-x64
```

This will copy folder contents to `/usr/local/stow/node/0.12.7`, delete stowed files from current version if any, link 0.12.7 to current, and stow files into `/usr/local`.

To delete stowed files, run *steeve* with command `unuse`:

```bash
$ sudo steeve unuse tig
```

To list packages, run command `ls` without arguments:

```bash
$ steeve ls
node
tig
```

To list package version, run command `ls` with package name:

```bash
$ steeve ls tig
  2.1
* 2.1.1
```

*steeve* marks current version with an asterisk as seen above.

To remove specific version of a package, run command `uninstall` with package name and version:

```bash
$ sudo steeve uninstall tig 2.1.1
```

This will delete stowed files if version 2.1.1 is current, and remove folder `2.1.1`.

Finally, to remove package with all its versions, run command `uninstall` with only a package name:

```bash
$ sudo steeve uninstall tig
```


## Thanks

Thanks to authors of [GoboLinux](http://gobolinux.org/) from which I borrowed the idea of package structure.
