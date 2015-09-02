from collections import namedtuple
import errno
import os
import shutil
import subprocess

import click


def validate_dir(ctx, param, value):
    if value is not None and ('/' in value or '\0' in value):
        raise click.BadParameter("must be a directory name.")
    if param.name == 'version' and value == 'current':
        raise click.BadParameter("must not be 'current'.")
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
@click.option('-v', '--verbose', envvar='STEEVE_VERBOSE', count=True,
              help="Increase verbosity")
@click.pass_context
def cli(ctx, dir, target, no_folding, verbose):
    ctx.obj = Steeve(dir, target, no_folding, verbose)


@cli.command(help="Install package from given folder.")
@click.argument('package', callback=validate_dir)
@click.argument('version', callback=validate_dir)
@click.argument('path')
@click.pass_obj
def install(steeve, package, version, path):
    steeve.install(package, version, path)


@cli.command(help="Reinstall package from given folder.")
@click.argument('package', callback=validate_dir)
@click.argument('version', callback=validate_dir)
@click.argument('path')
@click.pass_obj
def reinstall(steeve, package, version, path):
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
def stow(steeve, package, version):
    steeve.stow(package, version)


@cli.command(help="Delete stowed symlinks.")
@click.argument('package', callback=validate_dir)
@click.pass_obj
def unstow(steeve, package):
    steeve.unstow(package)


@cli.command(help="Restow (like unstow followed by stow).")
@click.argument('package', callback=validate_dir)
@click.pass_obj
def restow(steeve, package):
    steeve.restow(package)


@cli.command(help="List packages or package versions.")
@click.argument('package', required=False, callback=validate_dir)
@click.option('-q', '--quiet', is_flag=True,
              help="Display packages or versions without formatting.")
@click.pass_obj
def ls(steeve, package, quiet):
    steeve.ls(package, quiet)


class Steeve(namedtuple('Steeve', 'dir target no_folding verbose')):
    def install(self, package, version, path):
        try:
            shutil.copytree(path, self.package_path(package, version))
        except OSError as err:
            if err.errno == errno.ENOENT:
                click.secho("source path '{}' does not exist"
                            .format(path),
                            err=True, fg='red')
                return
            elif err.errno == errno.EEXIST and os.path.isdir(path):
                click.secho("the package '{}/{}' is already installed"
                            .format(package, version),
                            err=True, fg='red')
                return
            else:
                raise

        self.stow(package, version)

    def uninstall(self, package, version=None):
        if version is None:
            self.unstow(package)
            try:
                shutil.rmtree(self.package_path(package))
            except OSError as err:
                if err.errno == errno.ENOENT:
                    click.secho("package '{}' does not exist"
                                .format(package),
                                err=True, fg='red')
                    return
                else:
                    raise
        else:
            if version == self.current_version(package):
                self.unstow(package)
            try:
                shutil.rmtree(self.package_path(package, version))
            except OSError as err:
                if err.errno == errno.ENOENT:
                    click.secho("package '{}/{}' is not installed"
                                .format(package, version),
                                err=True, fg='red')
                    return
                else:
                    raise

            # Remove empty package folder
            if not os.listdir(self.package_path(package)):
                os.rmdir(self.package_path(package))

    def reinstall(self, package, version, path):
        self.uninstall(package, version)
        self.install(package, version, path)

    def stow(self, package, version):
        if not os.path.exists(self.package_path(package, version)):
            click.secho("package '{}/{}' is not installed"
                        .format(package, version),
                        err=True, fg='red')
            return

        self.unstow(package)
        self.link_current(package, version)
        try:
            options = []
            if self.no_folding:
                options.append('--no-folding')
            if self.verbose > 0:
                options.append('--verbose={}'.format(self.verbose))
            subprocess.check_call([
                'stow'
            ] + options + [
                '-t', self.target,
                '-d', self.package_path(package),
                'current'
            ])
        except subprocess.CalledProcessError as err:
            click.secho('stow returned code {}'
                        .format(err.returncode),
                        err=True, fg='red')

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
            click.secho('stow returned code {}'
                        .format(err.returncode),
                        err=True, fg='red')
        os.remove(self.package_path(package, 'current'))

    def restow(self, package):
        version = self.current_version(package)
        if version is None:
            click.secho("package '{}' is not stowed"
                        .format(package),
                        err=True, fg='red')
            return
        self.unstow(package)
        self.stow(package, version)

    def ls(self, package, quiet):
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
                    click.secho("no such package '{}'"
                                .format(package),
                                err=True, fg='red')
                    return
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

    def current_version(self, package):
        try:
            dst = os.readlink(self.package_path(package, 'current'))
        except OSError as err:
            if err.errno == errno.ENOENT:
                return None
            else:
                raise
        return os.path.basename(dst.rstrip('/'))

    def package_path(self, package, version=None):
        if version is None:
            return os.path.join(self.dir, package)
        else:
            return os.path.join(self.dir, package, version)


if __name__ == '__main__':
    cli()
