tornado-sqlalchemy
==================

.. image:: https://badge.fury.io/py/tornado-sqlalchemy.svg
    :target: https://pypi.python.org/pypi/tornado-sqlalchemy

.. image:: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy.svg?branch=stable
    :target: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy

.. image:: https://readthedocs.org/projects/tornado-sqlalchemy/badge/?version=latest
    :target: https://tornado-sqlalchemy.readthedocs.io/en/latest/


Python helpers for using SQLAlchemy_ with Tornado_.

Installation
------------

.. code-block:: bash

    $ pip install tornado-sqlalchemy

Usage
-----

.. code-block:: python

    from tornado.gen import coroutine
    from tornado.web import Application, RequestHandler
    from tornado_sqlalchemy import as_future, make_session_factory, SessionMixin

    class NativeCoroutinesRequestHandler(SessionMixin, RequestHandler):
        async def get(self):
            with self.make_session() as session:
                count = await as_future(session.query(UserModel).count)

            self.write('{} users so far!'.format(count))

    class GenCoroutinesRequestHandler(SessionMixin, RequestHandler):
        @coroutine
        def get(self):
            with self.make_session() as session:
                count = yield as_future(session.query(UserModel).count)

            self.write('{} users so far!'.format(count))

    class SynchronousRequestHandler(SessionMixin, RequestHandler):
        def get(self):
            with self.make_session() as session:
                count = session.query(UserModel).count()

            self.write('{} users so far!'.format(count))

    handlers = (
       (r'/native-coroutines', NativeCoroutinesRequestHandler),
       (r'/gen-coroutines', GenCoroutinesRequestHandler),
       (r'/sync', SynchronousRequestHandler),
    )

    app = Application(
       handlers,
       session_factory=make_session_factory('postgres://user:password@host/database')
    )

Documentation
-------------

Documentation is available at `Read The Docs`_.


Development
-----------

To work on this package, please make sure you have Python 3.5+ installed.

1. Git clone the repository -
   :code:`git clone https://github.com/siddhantgoel/tornado-sqlalchemy`

2. Install the packages required for development -
   :code:`make install-deps`

3. That's basically it. You should now be able to run the test suite -
   :code:`py.test tests/`.

.. _Read The Docs: https://tornado-sqlalchemy.readthedocs.io
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _tornado: http://tornadoweb.org
