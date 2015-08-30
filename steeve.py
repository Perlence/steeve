from __future__ import print_function

import errno
import os
from os.path import join
import shutil
import subprocess

import click


STOW_DIR = '/usr/local/stow'
STOW_TARGET = '/usr/local'


def validate_dir(ctx, param, value):
    if '/' in value or '\0' in value:
        raise click.BadParameter("must be a directory name."
                                 .format(param))
    return value


@click.group()
def cli():
    pass


@cli.command(help="Install package from given folder.")
@click.argument('package', callback=validate_dir)
@click.argument('version', callback=validate_dir)
@click.argument('path')
@click.option('-f', '--force', is_flag=True,
              help="Rewrite package contents.")
def install(package, version, path, force):
    package_path = join(STOW_DIR, package)
    package_version_path = join(STOW_DIR, package, version)

    try:
        makedirs(package_path, exist_ok=True)
    except OSError as err:
        if (err.errno == errno.EEXIST and os.path.isdir(path) and
                not force):
            click.echo(err)
            click.echo("the package '{}/{}' is already installed"
                       .format(package, version),
                       err=True)
            return
        else:
            raise
    shutil.copytree(path, package_version_path)

    unstow(package)
    link_current(package, version)
    stow(package)


@cli.command(help="Remove the whole package or specific version.")
@click.argument('package', callback=validate_dir)
@click.argument('version', required=False, callback=validate_dir)
def uninstall(package, version):
    if version is None:
        unstow(package)
        shutil.rmtree(join(STOW_DIR, package))
    else:
        current = current_version(package)
        if version == current:
            unstow(package)
        shutil.rmtree(join(STOW_DIR, package, version))
    # Remove empty package folder
    if not os.listdir(join(STOW_DIR, package)):
        os.rmdir(join(STOW_DIR, package))


@cli.command(help="Delete stowed symlinks.")
@click.argument('package', callback=validate_dir)
def unuse(package):
    unstow(package)


@cli.command(help="Stow given package version into target dir.")
@click.argument('package', callback=validate_dir)
@click.argument('version', callback=validate_dir)
def use(package, version):
    unstow(package)
    link_current(package, version)
    stow(package)


@cli.command(help="List packages or package versions.")
@click.argument('package', required=False, callback=validate_dir)
def ls(package):
    if package is None:
        packages = os.listdir(STOW_DIR)
        for package in packages:
            click.echo(package)
    else:
        try:
            versions = os.listdir(join(STOW_DIR, package))
        except OSError as err:
            if err.errno == errno.ENOENT:
                click.echo("no such package '{}'".format(package),
                           err=True)
                return
            else:
                raise
        try:
            versions.remove('current')
        except ValueError:
            pass
        current = current_version(package)
        for version in versions:
            used = '* ' if current == version else '  '
            click.echo(used + version)


def link_current(package, version):
    current = join(STOW_DIR, package, 'current')
    try:
        os.remove(current)
    except OSError as err:
        if err.errno != errno.ENOENT:
            raise
    os.symlink(join(STOW_DIR, package, version), current)


def current_version(package):
    try:
        dst = os.readlink(join(STOW_DIR, package, 'current'))
    except OSError as err:
        if err.errno == errno.ENOENT:
            return None
        else:
            raise
    return os.path.basename(dst)


def stow(package):
    try:
        subprocess.check_output([
            'stow',
            '-t', STOW_TARGET,
            '-d', join(STOW_DIR, package),
            'current'])
    except subprocess.CalledProcessError as err:
        click.echo('stow returned code {}: {}'
                   .format(err.returncode, err.output),
                   err=True)


def unstow(package):
    if current_version(package) is None:
        return
    try:
        subprocess.check_output([
            'stow',
            '-t', STOW_TARGET,
            '-d', join(STOW_DIR, package),
            '-D',
            'current'])
    except subprocess.CalledProcessError as err:
        click.echo('stow returned code {}: {}'
                   .format(err.returncode, err.output),
                   err=True)
    os.remove(join(STOW_DIR, package, 'current'))


def makedirs(name, mode=0o777, exist_ok=False):
    """makedirs(name [, mode=0o777][, exist_ok=False])

    Super-mkdir; create a leaf directory and all intermediate ones.  Works like
    mkdir, except that any intermediate path segment (not just the rightmost)
    will be created if it does not exist. If the target directory already
    exists, raise an OSError if exist_ok is False. Otherwise no exception is
    raised.  This is recursive.

    Shamelessly copied from Python 3.4.2 os module.
    """
    head, tail = os.path.split(name)
    if not tail:
        head, tail = os.path.split(head)
    if head and tail and not os.path.exists(head):
        try:
            makedirs(head, mode, exist_ok)
        except OSError, e:
            # be happy if someone already created the path
            if e.errno != errno.EEXIST:
                raise
        cdir = os.curdir
        if isinstance(tail, bytes):
            cdir = bytes(os.curdir, 'ASCII')
        if tail == cdir:           # xxx/newdir/. exists if xxx/newdir exists
            return
    try:
        os.mkdir(name, mode)
    except OSError as e:
        if not exist_ok or e.errno != errno.EEXIST or not os.path.isdir(name):
            raise


if __name__ == '__main__':
    cli()
