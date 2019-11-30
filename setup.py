from setuptools import setup
from os import path
import sys
import os

version = None

if sys.argv[-2] == '--version' and 'sdist' in sys.argv:
    version = sys.argv[-1]
    sys.argv.pop()
    sys.argv.pop()

if 'sdist' in sys.argv and not version:
    raise Exception("Please set a version with --version x.y.z")

if not version:
    if 'sdist' in sys.argv:
        raise Exception("Please set a version with --version x.y.z")
    else:
        path_pkg_info = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'PKG-INFO')
        if os.path.isfile(path_pkg_info):
            with open(path_pkg_info, 'r')as f:
                for l in f.readlines():
                    if 'Version' in l:
                        _, version = l.split(' ')
        else:
            print("WARNING: cannot set version in custom setup.py")

if version:
    version = version.strip()
print("version: %s" % version)

# read the contents of the README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pymacaron-unit',
    version=version,
    url='https://github.com/pymacaron/pymacaron-unit',
    license='BSD',
    author='Erwan Lemonnier',
    author_email='erwan@lemonnier.se',
    description='Library for unittesting json REST apis built with pymacaron',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'requests',
    ],
    tests_require=[
        'nose',
        'mock',
        'pycodestyle',
    ],
    test_suite='nose.collector',
    packages=['pymacaron_unit'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
