from setuptools import setup


with open('README.rst') as f:
    long_description = f.read()


setup(
    name='tornado_sqlalchemy',
    version='0.1.0',
    description='SQLAlchemy helpers for working in Tornado',
    long_description=long_description,
    author='Siddhant Goel',
    author_email='siddhantgoel@gmail.com',
    license='MIT',
    url='https://github.com/siddhantgoel/tornado-sqlalchemy',
    packages=['tornado_sqlalchemy'],
    keywords=['tornado', 'sqlalchemy']
)
