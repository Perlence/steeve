======
steeve
======

Tiny `GNU Stow <https://www.gnu.org/software/stow/>`__–based package manager.

.. contents::


Summary
=======

*steeve* is not a replacement for any full-fledged package manager like *dpkg*
or *rpm*, but instead an addition, designed to handle manually built software
and binary distributions.  Instead of polluting ``/usr/local`` with binaries
and libraries that aren't tracked by any package manager and thus cannot be
safely removed or upgraded, *steeve* provides a structured approach that allows
for managing multiple software versions in a matter of a command.


Packages
========

By default packages live in ``/usr/local/stow``.  This location is configured
either via environment variable ``STEEVE_DIR`` or command-line option ``-d``,
``--dir``. A package consists of one or multiple subdirectories named after
version.  Each version has directories with files that will be linked into
*target directory*, which is ``/usr/local`` by default.  Target directory can
be changed via environment variable ``STEEVE_TARGET`` or command-line option
``-t``, ``--target``.  The prominent part of a package is symbolic link named
``current`` that points to current version.

Here's an example of a valid package tree:

.. code-block:: bash

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


Tree Folding
============

The main gotcha is GNU Stow's tree folding mechanism.  Please, get accustomed
to it by reading chapter `Installing Packages
<http://www.gnu.org/software/stow/manual/stow.html#Installing-Packages>`__ of
GNU Stow manual.  You can disable folding by setting environment variable
``STEEVE_NO_FOLDING`` or passing ``--no-folding`` option.


Dependencies
============

- Python 2.7
- GNU Stow 2.2


Installation
============

Download a single-file executable from Github:

.. code-block:: bash

    curl -L https://github.com/Perlence/steeve/releases/download/v0.2/steeve_0.2_amd64 -o /usr/local/bin/steeve
    chmod +x /usr/local/bin/steeve

Or get the package from PyPI:

.. code-block:: bash

   pip install steeve

Or get the latest development version:

.. code-block:: bash

   git clone https://github.com/Perlence/steeve.git
   cd steeve
   pip install --editable .

To install bash completion, download the `script
<https://github.com/Perlence/steeve/blob/master/completion/steeve.bash>`__ and
source it from your ``.bashrc``.

To install fish completion, download the `script
<https://github.com/Perlence/steeve/blob/master/completion/steeve.fish>`__ and
put it in ``~/.config/fish/completions``.


Usage
=====

Run *steeve* with ``--help`` option to see the list of commands:

.. code-block:: bash

   $ steeve --help

To see usage of a command, run:

.. code-block:: bash

   $ steeve COMMAND --help

``stow``
--------

*steeve* helps you install manually built programs.  For example, to install
`tig <http://jonas.nitro.dk/tig/>`__, text-mode interface for git, first
download the release tarball:

.. code-block:: bash

   $ curl -LO http://jonas.nitro.dk/tig/releases/tig-2.1.1.tar.gz

Then configure, make and install with prefix:

.. code-block:: bash

   $ ./configure
   $ make prefix=/usr/local
   $ sudo make install prefix=/usr/local/stow/tig/2.1.1

Finally, stow tig 2.1.1 into ``/usr/local`` with *steeve*:

.. code-block:: bash

   $ sudo steeve stow tig 2.1.1

Under the covers ``steeve stow`` creates a symbolic link to current version and
runs ``stow`` to link contents of ``current`` into ``/usr/local``:

.. code-block:: bash

   $ sudo ln -s /usr/local/stow/tig/2.1.1 /usr/local/stow/tig/current
   $ sudo stow -t /usr/local -d tig current

To restow symbolic links, simply run ``steeve stow``:

.. code-block:: bash

   $ sudo steeve stow tig

``install``
-----------

Also *steeve* can manage binary distributions.  For instance, let's install
p4merge binaries:

.. code-block:: bash

   $ curl -LO http://cdist2.perforce.com/perforce/r15.2/bin.linux26x86_64/p4v.tgz
   $ tar xf p4v.tgz
   $ ls p4v-2015.2.1315639
   bin/  lib/

Now, install p4merge from directory with ``steeve install``:

.. code-block:: bash

   $ sudo steeve install p4v 2015.2.1315639 ./p4v-2015.2.1315639

This will copy folder contents to ``/usr/local/stow/p4v/2015.2.1315639``,
delete stowed files from current version if any, link 2015.2.1315639 to
current, and stow files into ``/usr/local``.

If you forgot to install some files, you can ``install`` the package once
again:

.. code-block:: bash

   $ sudo steeve install p4v 2015.2.1315639 ./p4v-2015.2.1315639

It's achieved by uninstalling the package followed by installing it again, so
*steeve* will prompt you before reinstalling.

``unstow``
----------

To delete stowed files, run *steeve* with command ``unstow``:

.. code-block:: bash

   $ sudo steeve unstow tig

``ls``
------

To list packages, run command ``ls`` without arguments:

.. code-block:: bash

   $ steeve ls
   node
   tig

To list package version, run command ``ls`` with package name:

.. code-block:: bash

   $ steeve ls tig
     2.1
   * 2.1.1

*steeve* marks current version with an asterisk as seen above.

``uninstall``
-------------

To remove specific version of a package, run command ``uninstall`` with package
name and version:

.. code-block:: bash

   $ sudo steeve uninstall tig 2.1.1

This will delete stowed files if version 2.1.1 is current, and remove folder
``2.1.1``.

Finally, to remove package with all its versions, run command ``uninstall``
with only a package name:

.. code-block:: bash

   $ sudo steeve uninstall tig


Thanks
======

Thanks to authors of `GoboLinux <http://gobolinux.org/>`__ from which I
borrowed the idea of package structure.

Thanks to Armin Ronacher and contributors for `Click
<http://click.pocoo.org/>`__ which is *\*click\** nice.
