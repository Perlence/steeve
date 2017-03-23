from collections import namedtuple
import errno
import os
import shutil
import subprocess

import click
from whichcraft import which

__version__ = '0.2'


def validate_dir(ctx, param, value):
    if value is not None and (os.path.sep in value or '\0' in value):
        raise click.BadParameter("must be a directory name.")
    if param.name == 'version' and value == 'current':
        raise click.BadParameter("must not be 'current'.")
    return value


def show_version(ctx, param, value):
    if not value:
        return
    click.echo('click ' + __version__)
    ctx.exit()


def check_stow():
    if which('stow') is None:
        raise click.ClickException("GNU Stow is not installed")


required_package_argument = click.argument(
    'package', callback=validate_dir)
required_packages_argument = click.argument(
    'packages', nargs=-1, callback=validate_dir)
package_argument = click.argument(
    'package', required=False, callback=validate_dir)
required_version_argument = click.argument(
    'version', callback=validate_dir)
version_argument = click.argument(
    'version', required=False, callback=validate_dir)
required_path_argument = click.argument('path', type=click.Path(exists=True))

yes_option = click.option(
    '-y', '--yes', is_flag=True,
    help="Assume Yes to all queries and do not prompt.")


@click.group()
@click.option('-d', '--dir', envvar='STEEVE_DIR', metavar='DIR',
              default='/usr/local/stow',
              help="Set location of packages to DIR.")
@click.option('-t', '--target', envvar='STEEVE_TARGET', metavar='DIR',
              default=None,
              help="Set stow target to DIR (default is parent of stow dir).")
@click.option('--no-folding', envvar='STEEVE_NO_FOLDING', is_flag=True,
              help="Disable folding of newly stowed directories.")
@click.option('-v', '--verbose', envvar='STEEVE_VERBOSE', count=True,
              help="Increase verbosity.")
@click.option('--version', is_flag=True, callback=show_version,
              expose_value=False,
              help="Show version and exit.")
@click.pass_context
def cli(ctx, dir, target, no_folding, verbose):
    dir = os.path.abspath(dir)
    if target is None:
        target = os.path.dirname(dir)
    ctx.obj = Steeve(dir, target, no_folding, verbose)


@cli.command(help="Install/reinstall package from given folder.")
@required_package_argument
@required_version_argument
@required_path_argument
@yes_option
@click.pass_obj
def install(steeve, package, version, path, yes):
    check_stow()
    steeve.install(package, version, path, yes)


@cli.command(help="Remove the whole package or specific version.")
@yes_option
@required_package_argument
@version_argument
@click.pass_obj
def uninstall(steeve, package, version, yes):
    check_stow()
    steeve.uninstall(package, version, yes)


@cli.command(help="Stow/restow given version into target dir.")
@required_package_argument
@required_version_argument
@click.pass_obj
def stow(steeve, package, version):
    check_stow()
    steeve.stow(package, version)


@cli.command(help="Delete stowed symlinks.")
@required_packages_argument
@click.pass_obj
def unstow(steeve, packages):
    check_stow()
    for package in packages:
        steeve.unstow(package, strict=True)


@cli.command(help="List packages or package versions.")
@package_argument
@click.option('-q', '--quiet', is_flag=True,
              help="Display packages or versions without formatting.")
@click.pass_obj
def ls(steeve, package, quiet):
    steeve.ls(package, quiet)


class Steeve(namedtuple('Steeve', 'dir target no_folding verbose')):
    def install(self, package, version, path, yes=False):
        if self.package_exists(package, version):
            self.uninstall_version(package, version, yes, reinstall=True)

        try:
            shutil.copytree(path, self.package_path(package, version))
        except OSError as err:
            if err.errno == errno.ENOENT:
                raise click.ClickException(
                    "source path '{}' does not exist"
                    .format(path))
            elif err.errno == errno.EEXIST and os.path.isdir(path):
                raise click.ClickException(
                    "the package '{}/{}' is already installed"
                    .format(package, version))
            else:
                raise

        self.stow(package, version)

    def uninstall(self, package, version=None, yes=False):
        if not self.package_exists(package, version):
            if version is not None:
                raise click.ClickException(
                    "the package '{}/{}' is not installed"
                    .format(package, version))
            else:
                raise click.ClickException(
                    "the package '{}' is not installed"
                    .format(package))

        if version is not None:
            self.uninstall_version(package, version, yes)
        else:
            self.uninstall_package(package, yes)

    def uninstall_package(self, package, yes=False):
        if not yes:
            click.echo("Uninstalling '{}' and all its versions:"
                       .format(package))
            self.ls(package)
            click.confirm('Proceed?', abort=True)

        self.unstow(package)
        try:
            shutil.rmtree(self.package_path(package))
        except OSError as err:
            if err.errno == errno.ENOENT:
                raise click.ClickException(
                    "package '{}' does not exist"
                    .format(package))
            else:
                raise

    def uninstall_version(self, package, version, yes=False, reinstall=False):
        if not yes:
            action = 'reinstall' if reinstall else 'uninstall'
            click.confirm(
                "Are you sure you want to {} package '{}/{}'?"
                .format(action, package, version),
                abort=True)

        if version == self.current_version(package):
            self.unstow(package)

        try:
            shutil.rmtree(self.package_path(package, version))
        except OSError as err:
            if err.errno == errno.ENOENT:
                raise click.ClickException(
                    "package '{}/{}' is not installed"
                    .format(package, version))
            else:
                raise

        # Remove empty package folder
        if not os.listdir(self.package_path(package)):
            os.rmdir(self.package_path(package))

    def stow(self, package, version):
        if not os.path.exists(self.package_path(package, version)):
            raise click.ClickException(
                "package '{}/{}' is not installed"
                .format(package, version))

        self.unstow(package)
        self.link_current(package, version)
        options = []
        if self.no_folding:
            options.append('--no-folding')
        if self.verbose > 0:
            options.append('--verbose={}'.format(self.verbose))
        status = subprocess.call([
            'stow'
        ] + options + [
            '-t', self.target,
            '-d', self.package_path(package),
            'current',
        ])
        if status:
            self.remove_current(package)
            raise click.ClickException(
                'stow returned code {}'
                .format(status))

    def unstow(self, package, strict=False):
        if self.current_version(package) is None:
            if strict:
                raise click.ClickException(
                    "package '{}' is not stowed"
                    .format(package))
            else:
                return

        status = subprocess.call([
            'stow',
            '-t', self.target,
            '-d', self.package_path(package),
            '-D',
            'current',
        ])
        if status:
            raise click.ClickException(
                'stow returned code {}'
                .format(status))
        self.remove_current(package)

    def ls(self, package=None, quiet=False):
        if package is None:
            try:
                packages = os.listdir(self.dir)
            except OSError as err:
                if err.errno == errno.ENOENT:
                    return
                else:
                    raise

            for package in packages:
                click.echo(package)
        else:
            try:
                versions = os.listdir(self.package_path(package))
            except OSError as err:
                if err.errno == errno.ENOENT:
                    raise click.ClickException(
                        "no such package '{}'"
                        .format(package))
                else:
                    raise
            try:
                versions.remove('current')
            except ValueError:
                pass
            current = self.current_version(package)
            for version in versions:
                if not quiet:
                    used = '* ' if current == version else '  '
                else:
                    used = ''
                click.echo(used + version)

    def link_current(self, package, version):
        current = self.package_path(package, 'current')
        try:
            os.remove(current)
        except OSError as err:
            if err.errno != errno.ENOENT:
                raise
        os.symlink(self.package_path(package, version), current)

    def remove_current(self, package):
        os.remove(self.package_path(package, 'current'))

    def current_version(self, package):
        try:
            dst = os.readlink(self.package_path(package, 'current'))
        except OSError as err:
            if err.errno == errno.ENOENT:
                return
            else:
                raise
        return os.path.basename(dst.rstrip(os.path.sep))

    def package_exists(self, package, version=None):
        path = self.package_path(package, version)
        return os.path.exists(path)

    def package_path(self, package, version=None):
        if version is None:
            return os.path.join(self.dir, package)
        else:
            return os.path.join(self.dir, package, version)

if __name__ == '__main__':
    cli()
