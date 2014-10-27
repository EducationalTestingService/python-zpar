#!/usr/bin/env python

# Adapted from https://github.com/Turbo87/py-xcsoar/blob/master/setup.py

import os
from setuptools import setup
from setuptools.command.install import install
from distutils.command.build import build
from subprocess import call

import sys

BASEPATH = os.path.dirname(os.path.abspath(__file__))
ZPAR_PATH = os.path.join(BASEPATH, 'zpar')
ZPAR_LIB_PATH = os.path.join(ZPAR_PATH, 'dist')

def readme():
    with open('README.rst') as f:
        return f.read()

class build_zpar(build):
    def run(self):

        # run original build code
        build.run(self)

        # get a copy of the user environment
        env = os.environ.copy()

        sys.stderr.write('running build_zpar\n')

        # for now the compilation is just calling make
        # with the option to override the CXX defined
        # in the zpar Makefile with the CXX environment
        # variable if defined.
        if os.environ.get('CXX'):
            cmd = ['make', '-e']
            env['CXX'] = os.environ.get('CXX')
        else:
            cmd = ['make']

        # compile the shared library path
        def compile():
            sys.stderr.write('*' * 80 + '\n')
            ret = call(cmd, env=env)
            # if something went wrong, raise an error
            if ret:
                raise RuntimeError('ZPar shared library compilation failed')
            sys.stderr.write('*' * 80 + '\n')
        self.execute(compile, [], 'compiling zpar library')

        # copy resulting tool to library build folder
        self.mkpath(self.build_lib)

        if not self.dry_run:
            self.copy_tree(ZPAR_PATH, self.build_lib)

class install_zpar(install):

    def initialize_options(self):
        install.initialize_options(self)
        self.build_scripts = None

    def finalize_options(self):
        install.finalize_options(self)
        self.set_undefined_options('build', ('build_scripts', 'build_scripts'))

    def run(self):
        # run original install code
        install.run(self)

        # install ZPar executables
        sys.stderr.write('running install_zpar\n')
        install_path = os.path.join(self.install_lib, 'zpar')
        self.mkpath(install_path)
        self.copy_tree(self.build_lib, install_path)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='python-zpar',
    version='0.5',
    description='A Wrapper around the ZPar statistical tagger/parser for English',
    maintainer='Nitin Madnani',
    maintainer_email='nmadnani@ets.org',
    license='MIT',
    url='http://www.github.com/EducationalTestingService/python-zpar',
    long_description=readme(),
    classifiers=['Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Topic :: Software Development',
                 'Topic :: Scientific/Engineering',
                 'Operating System :: POSIX',
                 'Operating System :: Unix',
                 'Operating System :: MacOS',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.3',
                ],
    cmdclass={
        'build': build_zpar,
        'install': install_zpar,
    }
)
