from __future__ import print_function

import errno
import os
from os.path import join
import shutil
import subprocess
from collections import namedtuple

import click


def validate_dir(ctx, param, value):
    if value is not None and ('/' in value or '\0' in value):
        raise click.BadParameter("must be a directory name.")
    return value


@click.group()
@click.option('-d', '--dir', metavar='DIR', default='/usr/local/stow',
              help="Set location of packages to DIR.")
@click.option('-t', '--target', metavar='DIR', default='/usr/local',
              help="Set stow target to DIR.")
@click.option('--no-folding', is_flag=True,
              help="Disable folding of newly stowed directories.")
@click.pass_context
def cli(ctx, dir, target, no_folding):
    ctx.obj = Steeve(dir, target, no_folding)


@cli.command(help="Install package from given folder.")
@click.argument('package', callback=validate_dir)
@click.argument('version', callback=validate_dir)
@click.argument('path')
@click.option('-f', '--force', is_flag=True,
              help="Rewrite package contents.")
@click.pass_obj
def install(steeve, package, version, path, force):
    package_path = join(steeve.dir, package)
    package_version_path = join(steeve.dir, package, version)

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

    steeve.unstow(package)
    steeve.link_current(package, version)
    steeve.stow(package)


@cli.command(help="Remove the whole package or specific version.")
@click.argument('package', callback=validate_dir)
@click.argument('version', required=False, callback=validate_dir)
@click.pass_obj
def uninstall(steeve, package, version):
    if version is None:
        steeve.unstow(package)
        shutil.rmtree(join(steeve.dir, package))
    else:
        current = steeve.current_version(package)
        if version == current:
            steeve.unstow(package)
        shutil.rmtree(join(steeve.dir, package, version))

        # Remove empty package folder
        if not os.listdir(join(steeve.dir, package)):
            os.rmdir(join(steeve.dir, package))


@cli.command(help="Stow given package version into target dir.")
@click.argument('package', callback=validate_dir)
@click.argument('version', callback=validate_dir)
@click.pass_obj
def use(steeve, package, version):
    if not os.path.exists(join(steeve.dir, package, version)):
        click.echo("package '{}/{}' is not installed"
                   .format(package, version),
                   err=True)
        return

    steeve.unstow(package)
    steeve.link_current(package, version)
    steeve.stow(package)


@cli.command(help="Delete stowed symlinks.")
@click.argument('package', callback=validate_dir)
@click.pass_obj
def unuse(steeve, package):
    steeve.unstow(package)


@cli.command(help="List packages or package versions.")
@click.argument('package', required=False, callback=validate_dir)
@click.pass_obj
def ls(steeve, package):
    if package is None:
        packages = os.listdir(steeve.dir)
        for package in packages:
            click.echo(package)
    else:
        try:
            versions = os.listdir(join(steeve.dir, package))
        except OSError as err:
            if err.errno == errno.ENOENT:
                click.echo("no such package '{}'"
                           .format(package),
                           err=True)
                return
            else:
                raise
        try:
            versions.remove('current')
        except ValueError:
            pass
        current = steeve.current_version(package)
        for version in versions:
            used = '* ' if current == version else '  '
            click.echo(used + version)


StowOptionsTuple = namedtuple('StowOptionsTuple', 'dir, target, no_folding')


class Steeve(StowOptionsTuple):
    def link_current(self, package, version):
        current = join(self.dir, package, 'current')
        try:
            os.remove(current)
        except OSError as err:
            if err.errno != errno.ENOENT:
                raise
        os.symlink(join(self.dir, package, version), current)

    def current_version(self, package):
        try:
            dst = os.readlink(join(self.dir, package, 'current'))
        except OSError as err:
            if err.errno == errno.ENOENT:
                return None
            else:
                raise
        return os.path.basename(dst)

    def stow(self, package):
        try:
            args = [
                'stow',
                '-t', self.target,
                '-d', join(self.dir, package),
                'current'
            ]
            if self.no_folding:
                args.insert(1, '--no-folding')
            subprocess.check_output(args)
        except subprocess.CalledProcessError as err:
            click.echo('stow returned code {}'
                       .format(err.returncode),
                       err=True)

    def unstow(self, package):
        if self.current_version(package) is None:
            return
        try:
            subprocess.check_output([
                'stow',
                '-t', self.target,
                '-d', join(self.dir, package),
                '-D',
                'current'])
        except subprocess.CalledProcessError as err:
            click.echo('stow returned code {}'
                       .format(err.returncode),
                       err=True)
        os.remove(join(self.dir, package, 'current'))


def makedirs(name, mode=0o777, exist_ok=False):
    """makedirs(name [, mode=0o777][, exist_ok=False])

    Super-mkdir; create a leaf directory and all intermediate ones.
    Works like mkdir, except that any intermediate path segment (not
    just the rightmost) will be created if it does not exist.  If the
    target directory already exists, raise an OSError if exist_ok is
    False. Otherwise no exception is raised.  This is recursive.

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
        if tail == cdir:  # xxx/newdir/. exists if xxx/newdir exists
            return
    try:
        os.mkdir(name, mode)
    except OSError as e:
        if not exist_ok or e.errno != errno.EEXIST or not os.path.isdir(name):
            raise


if __name__ == '__main__':
    cli()
