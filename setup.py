# -*- encoding: UTF-8 -*
from setuptools import setup

with open('README.md') as fp:
    README = fp.read()

setup(
    name='steeve',
    version='0.1',
    author='Sviatoslav Abakumov',
    author_email='dust.harvesting@gmail.com',
    description=u'Tiny GNU Stow–based package manager',
    long_description=README,
    url='https://github.com/Perlence/steeve',
    download_url='https://github.com/Perlence/steeve/archive/master.zip',
    py_modules=['steeve'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'steeve = steeve:cli',
        ],
    },
    install_requires=[
        'click',
    ],
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
