# tornado-sqlalchemy

[![image](https://travis-ci.org/siddhantgoel/tornado-sqlalchemy.svg?branch=stable)](https://travis-ci.org/siddhantgoel/tornado-sqlalchemy)

[![image](https://badge.fury.io/py/tornado-sqlalchemy.svg)](https://pypi.python.org/pypi/tornado-sqlalchemy)

[![image](https://readthedocs.org/projects/tornado-sqlalchemy/badge/?version=latest)](https://tornado-sqlalchemy.readthedocs.io/en/latest/)

[![image](https://img.shields.io/pypi/pyversions/tornado-sqlalchemy.svg)](https://pypi.python.org/pypi/tornado-sqlalchemy)

Python helpers for using [SQLAlchemy] with [Tornado].

## Installation

```sh
$ pip install tornado-sqlalchemy
```

In case you prefer installing from the Github repository, please note that `main` is the
development branch so `stable` is what you should be installing from.

## Usage

```python
from tornado.gen import coroutine
from tornado.web import Application, RequestHandler
from tornado_sqlalchemy import as_future, SessionMixin, SQLAlchemy

class NativeCoroutinesRequestHandler(SessionMixin, RequestHandler):
    async def get(self):
        with self.make_session() as session:
            count = await as_future(session.query(User).count)

        self.write('{} users so far!'.format(count))

class GenCoroutinesRequestHandler(SessionMixin, RequestHandler):
    @coroutine
    def get(self):
        with self.make_session() as session:
            count = yield as_future(session.query(User).count)

        self.write('{} users so far!'.format(count))

class SynchronousRequestHandler(SessionMixin, RequestHandler):
    def get(self):
        with self.make_session() as session:
            count = session.query(User).count()

        self.write('{} users so far!'.format(count))

handlers = (
   (r'/native-coroutines', NativeCoroutinesRequestHandler),
   (r'/gen-coroutines', GenCoroutinesRequestHandler),
   (r'/sync', SynchronousRequestHandler),
)

app = Application(
   handlers,
   db=SQLAlchemy('postgres://user:password@host/database')
)
```

## Documentation

Documentation is available at [Read The Docs].


## Development

Please make sure you have Python 3.8+ and [Poetry] installed.

Since we run tests against multiple databases (currently MySQL, PostgreSQL, and
SQLite), we use [docker-compose] to make our lives easier.

1. Git clone the repository -
   `git clone https://github.com/siddhantgoel/tornado-sqlalchemy`

2. Install the packages required for development -
   `poetry install`

3. Ensure that the MySQL and PostgreSQL services (containers) are up -
   `docker-compose up -d`

4. That should basically be it. You should now be able to run the test suite -
   `poetry run py.test tests/`.

[docker-compose]: https://docs.docker.com/compose/
[Poetry]: https://poetry.eustace.io/
[Read The Docs]: https://tornado-sqlalchemy.readthedocs.io/en/stable/
[SQLAlchemy]: http://www.sqlalchemy.org/
[tornado]: https://www.tornadoweb.org/en/stable/
