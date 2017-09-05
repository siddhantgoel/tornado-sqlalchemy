# -*- coding: utf-8 -*-

import codecs
import os
import sys
from shutil import rmtree

from setuptools import setup, Command


pwd = os.path.abspath(os.path.dirname(__file__))


with codecs.open(os.path.join(pwd, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


def install_requires():
    deps = [
        'tornado >= 4.0',
        'SQLAlchemy >= 1.0'
    ]

    if sys.version_info.major == 2:
        deps.append('futures >= 3.0.0')

    return deps


class PublishCommand(Command):
    """Support setup.py publish.

    https://github.com/kennethreitz/setup.py/blob/master/setup.py
    """

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.sep.join(('.', 'dist')))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system(
            '{0} setup.py sdist bdist_wheel --universal'.format(
                sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


setup(
    name='tornado_sqlalchemy',
    version='0.3.2',
    description='SQLAlchemy helpers for working in Tornado',
    long_description=long_description,
    author='Siddhant Goel',
    author_email='siddhantgoel@gmail.com',
    license='MIT',
    url='https://github.com/siddhantgoel/tornado-sqlalchemy',
    packages=['tornado_sqlalchemy'],
    keywords=['tornado', 'sqlalchemy'],
    install_requires=install_requires(),
    cmdclass={
        'publish': PublishCommand
    }
)
