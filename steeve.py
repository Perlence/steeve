from collections import namedtuple
import errno
import os
import shutil
import subprocess

import click


def validate_dir(ctx, param, value):
    if value is not None and ('/' in value or '\0' in value):
        raise click.BadParameter("must be a directory name.")
    return value


@click.group()
@click.option('-d', '--dir', envvar='STEEVE_DIR', metavar='DIR',
              default='/usr/local/stow',
              help="Set location of packages to DIR.")
@click.option('-t', '--target', envvar='STEEVE_TARGET', metavar='DIR',
              default='/usr/local',
              help="Set stow target to DIR.")
@click.option('--no-folding', envvar='STEEVE_NO_FOLDING', is_flag=True,
              help="Disable folding of newly stowed directories.")
@click.pass_context
def cli(ctx, dir, target, no_folding):
    ctx.obj = Steeve(dir, target, no_folding)


@cli.command(help="Install package from given folder.")
@click.argument('package', callback=validate_dir)
@click.argument('version', callback=validate_dir)
@click.argument('path')
@click.pass_obj
def install(steeve, package, version, path):
    steeve.install(package, version, path)


@cli.command(help="Remove the whole package or specific version.")
@click.argument('package', callback=validate_dir)
@click.argument('version', required=False, callback=validate_dir)
@click.pass_obj
def uninstall(steeve, package, version):
    steeve.uninstall(package, version)


@cli.command(help="Stow given package version into target dir.")
@click.argument('package', callback=validate_dir)
@click.argument('version', callback=validate_dir)
@click.pass_obj
def use(steeve, package, version):
    steeve.use(package, version)


@cli.command(help="Delete stowed symlinks.")
@click.argument('package', callback=validate_dir)
@click.pass_obj
def unuse(steeve, package):
    steeve.unstow(package)


@cli.command(help="List packages or package versions.")
@click.argument('package', required=False, callback=validate_dir)
@click.pass_obj
def ls(steeve, package):
    steeve.ls(package)


class Steeve(namedtuple('Steeve', 'dir target no_folding')):
    def install(self, package, version, path):
        try:
            shutil.copytree(path, self.package_path(package, version))
        except OSError as err:
            if err.errno == errno.EEXIST and os.path.isdir(path):
                click.echo("the package '{}/{}' is already installed"
                           .format(package, version),
                           err=True)
                return
            else:
                raise

        self.use(package, version)

    def uninstall(self, package, version):
        if version is None:
            self.unstow(package)
            shutil.rmtree(self.package_path(package))
        else:
            if version == self.current_version(package):
                self.unstow(package)
            shutil.rmtree(self.package_path(package, version))

            # Remove empty package folder
            if not os.listdir(self.package_path(package)):
                os.rmdir(self.package_path(package))

    def use(self, package, version):
        if not os.path.exists(self.package_path(package, version)):
            click.echo("package '{}/{}' is not installed"
                       .format(package, version),
                       err=True)
            return

        self.unstow(package)
        self.link_current(package, version)
        self.stow(package)

    def ls(self, package):
        if package is None:
            packages = os.listdir(self.dir)
            for package in packages:
                click.echo(package)
        else:
            try:
                versions = os.listdir(self.package_path(package))
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
            current = self.current_version(package)
            for version in versions:
                used = '* ' if current == version else '  '
                click.echo(used + version)

    def link_current(self, package, version):
        current = self.package_path(package, 'current')
        try:
            os.remove(current)
        except OSError as err:
            if err.errno != errno.ENOENT:
                raise
        os.symlink(self.package_path(package, version), current)

    def current_version(self, package):
        try:
            dst = os.readlink(self.package_path(package, 'current'))
        except OSError as err:
            if err.errno == errno.ENOENT:
                return None
            else:
                raise
        return os.path.basename(dst.rstrip('/'))

    def stow(self, package):
        try:
            args = [
                'stow',
                '-t', self.target,
                '-d', self.package_path(package),
                'current'
            ]
            if self.no_folding:
                args.insert(1, '--no-folding')
            subprocess.check_call(args)
        except subprocess.CalledProcessError as err:
            click.echo('stow returned code {}'
                       .format(err.returncode),
                       err=True)

    def unstow(self, package):
        if self.current_version(package) is None:
            return
        try:
            subprocess.check_call([
                'stow',
                '-t', self.target,
                '-d', self.package_path(package),
                '-D',
                'current'])
        except subprocess.CalledProcessError as err:
            click.echo('stow returned code {}'
                       .format(err.returncode),
                       err=True)
        os.remove(self.package_path(package, 'current'))

    def package_path(self, package, version=None):
        if version is None:
            return os.path.join(self.dir, package)
        else:
            return os.path.join(self.dir, package, version)


if __name__ == '__main__':
    cli()
