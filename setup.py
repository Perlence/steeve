# -*- encoding: UTF-8 -*
from setuptools import setup

long_description = """\
steeve is not a replacement for any full-fledged package manager like *dpkg* or
*rpm*, but instead an addition, designed to handle manually built software and
binary distributions. Instead of polluting ``/usr/local`` with binaries and
libraries that aren't tracked by any package manager and thus cannot be safely
removed or upgraded, *steeve* provides a structured approach that allows for
managing multiple software versions in a matter of a command."""

setup(
    name='steeve',
    version='0.2',
    author='Sviatoslav Abakumov',
    author_email='dust.harvesting@gmail.com',
    description=u'Tiny GNU Stow–based package manager',
    long_description=long_description,
    url='https://github.com/Perlence/steeve',
    download_url='https://github.com/Perlence/steeve/archive/master.zip',
    py_modules=['steeve'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'steeve = steeve:cli',
        ],
    },
    install_requires=['click'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ]
)
