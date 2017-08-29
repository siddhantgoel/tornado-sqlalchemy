import codecs
import os
from sys import version_info

from setuptools import setup


pwd = os.path.abspath(os.path.dirname(__file__))


with codecs.open(os.path.join(pwd, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


def install_requires():
    deps = [
        'tornado >= 4.0',
        'SQLAlchemy >= 1.0'
    ]

    if version_info.major == 2:
        deps.append('futures >= 3.0.0')

    return deps


setup(
    name='tornado_sqlalchemy',
    version='0.2.2',
    description='SQLAlchemy helpers for working in Tornado',
    long_description=long_description,
    author='Siddhant Goel',
    author_email='siddhantgoel@gmail.com',
    license='MIT',
    url='https://github.com/siddhantgoel/tornado-sqlalchemy',
    packages=['tornado_sqlalchemy'],
    keywords=['tornado', 'sqlalchemy'],
    install_requires=install_requires()
)
