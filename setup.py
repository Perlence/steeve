from setuptools import setup

# with open('README.md') as fp:
#     README = fp.read()

setup(
    name='steeve',
    version='1.0',
    author='Sviatoslav Abakumov',
    author_email='dust.harvesting@gmail.com',
    # description='',
    # long_description=README,
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
        # 'Development Status :: 3 - Stable',
        # 'Environment :: Console',
    ]
)
