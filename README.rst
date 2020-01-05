tornado-sqlalchemy
==================

.. image:: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy.svg?branch=stable
    :target: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy

.. image:: https://badge.fury.io/py/tornado-sqlalchemy.svg
    :target: https://pypi.python.org/pypi/tornado-sqlalchemy

.. image:: https://readthedocs.org/projects/tornado-sqlalchemy/badge/?version=latest
    :target: https://tornado-sqlalchemy.readthedocs.io/en/latest/

.. image:: https://img.shields.io/pypi/pyversions/tornado-sqlalchemy.svg
    :target: https://pypi.python.org/pypi/tornado-sqlalchemy


Python helpers for using SQLAlchemy_ with Tornado_.

Installation
------------

.. code-block:: bash

    $ pip install tornado-sqlalchemy

In case you prefer installing from the Github repository, please note that
:code:`master` is the development branch so :code:`stable` is what you should be
installing from.

Usage
-----

.. code-block:: python

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

Documentation
-------------

Documentation is available at `Read The Docs`_.


Development
-----------

To work on this package, please make sure you have Python 3.5+ and Poetry_
installed.

1. Git clone the repository -
   :code:`git clone https://github.com/siddhantgoel/tornado-sqlalchemy`

2. Install the packages required for development -
   :code:`poetry install`

3. That should basically be it. Some tests rely on :code:`PostgreSQL` and
   :code:`MySQL`, so depending on which tests you run, setting those up could
   also be necessary. The required SQL scripts that setup the databases/owners
   are in the :code:`tests/travis/` folder.

4. You should now be able to run the test suite - :code:`poetry run py.test
   tests/`.

.. _Poetry: https://poetry.eustace.io/
.. _Read The Docs: https://tornado-sqlalchemy.readthedocs.io/en/stable/
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _tornado: https://www.tornadoweb.org/en/stable/
