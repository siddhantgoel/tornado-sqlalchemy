from setuptools import setup
from sys import version_info


with open('README.rst') as f:
    long_description = f.read()


install_requires = ['futures >== 3.0.0'] if version_info.major == 2 else []


setup(
    name='tornado_sqlalchemy',
    version='0.1.1',
    description='SQLAlchemy helpers for working in Tornado',
    long_description=long_description,
    author='Siddhant Goel',
    author_email='siddhantgoel@gmail.com',
    license='MIT',
    url='https://github.com/siddhantgoel/tornado-sqlalchemy',
    packages=['tornado_sqlalchemy'],
    keywords=['tornado', 'sqlalchemy'],
    install_requires=install_requires
)
