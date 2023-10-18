tornado-sqlalchemy
==================

.. image:: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy.svg?branch=master
    :target: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy

.. image:: https://badge.fury.io/py/tornado-sqlalchemy.svg
    :target: https://pypi.python.org/pypi/tornado-sqlalchemy

.. image:: https://img.shields.io/pypi/pyversions/tornado-sqlalchemy.svg
    :target: https://pypi.python.org/pypi/tornado-sqlalchemy

**tornado-sqlalchemy** is a Python library aimed at providing support for using
the SQLAlchemy_ database toolkit in tornado_ web applications.

Installation
------------

.. code-block:: bash

    $ pip install tornado-sqlalchemy

User Guide
----------

Motivation
~~~~~~~~~~

.. role:: strike
    :class: strike

:code:`tornado-sqlalchemy` handles the following problems/use-cases:

- **Boilerplate** - Tornado does not bundle code to handle database connections.
  So developer building apps using Tornado end up writing their own code - code
  to establish database connections, initialize engines, get/teardown sessions,
  and so on.

- **Database migrations** - Since you're using SQLAlchemy, you're probably also
  using alembic_ for database migrations. This again brings us to the point
  about boilerplate. If you're currently using SQLAlchemy with Tornado and have
  migrations set up using alembic, you likely have custom code written
  somewhere.

- **Asynchronous query execution** - ORMs are `poorly suited for explicit
  asynchronous programming`_. You don't know what property access or what method
  call would end up hitting the database. In such situations, it's a good idea
  to decide on *exactly what* you want to execute asynchronously.

The intention here is to have answers to all three of these in a
`standardized library`_ which can act as a central place for all the
:strike:`bugs` features, and hopefully can establish best practices.

Quickstart
~~~~~~~~~~

First, construct a :code:`SQLAlchemy` object and pass it to your
:code:`tornado.web.Application`.

.. code-block:: python

    from tornado.web import Application
    from tornado_sqlalchemy import SQLAlchemy

    from my_app.handlers import IndexHandler

    app = Application(
        ((r'/', IndexHandler),),
        db=SQLAlchemy(database_url)
     )

Next, when defining database models, make sure that your SQLAlchemy models are
inheriting from :code:`tornado_sqlalchemy.SQLAlchemy.Model`.

.. code-block:: python

    from sqlalchemy import Column, BigInteger, String
    from tornado_sqlalchemy import SQLAlchemy

    db = SQLAlchemy(url=database_url)

    class User(db.Model):
        id = Column(BigInteger, primary_key=True)
        username = Column(String(255), unique=True)

Finally, add :code:`SessionMixin` to your request handlers, which makes the
:code:`make_session` function available in the HTTP handler functions defined in
those request handlers.

As a convenience, :code:`SessionMixin` also provides a :code:`self.session`
property, which (lazily) builds and returns a new session object. This session
is then automatically closed when the request is finished.

.. code-block:: python

    from tornado_sqlalchemy import SessionMixin

    class SomeRequestHandler(SessionMixin, RequestHandler):
        def get(self):
            with self.make_session() as session:
                count = session.query(User).count()

            # alternatively,
            count = self.session.query(User).count()

            self.write('{} users so far!'.format(count))

To run database queries in the background, use the :code:`as_future` function to
wrap the SQLAlchemy Query_ into a Future_ object, which you can :code:`await` on
or :code:`yield` to get the result.

.. code-block:: python

    from tornado.gen import coroutine
    from tornado_sqlalchemy import SessionMixin, as_future

    class OldCoroutineRequestHandler(SessionMixin, RequestHandler):
        @coroutine
        def get(self):
            with self.make_session() as session:
                count = yield as_future(session.query(User).count)

            self.write('{} users so far!'.format(count))

    class NativeCoroutineRequestHandler(SessionMixin, RequestHandler):
        async def get(self):
            with self.make_session() as session:
                count = await as_future(session.query(User).count)

            self.write('{} users so far!'.format(count))

For a complete example, please refer to `examples/basic.py`.

Multiple Databases
~~~~~~~~~~~~~~~~~~

The :code:`SQLAlchemy` constructor supports multiple database URLs, using
SQLAlchemy ":code:`binds`".

The following example specifies three database connections, with
:code:`database_url` as the default, and :code:`foo`/:code:`bar` being the other
two connections.

.. code-block:: python

    from tornado.web import Application
    from tornado_sqlalchemy import SQLAlchemy

    from my_app.handlers import IndexHandler

    app = Application(
        ((r'/', IndexHandler),),
        db=SQLAlchemy(
            database_url, binds={'foo': foo_url, 'bar': bar_url}
        )
    )

Modify your model definitions with a :code:`__bind_key__` parameter.

.. code-block:: python

   from sqlalchemy import BigInteger, Column, String
   from tornado_sqlalchemy import SQLAlchemy

   db = SQLAlchemy(url=database_url, binds={'foo': foo_url, 'bar': bar_url})

   class Foo(db.Model):
      __bind_key__ = 'foo'
      __tablename__ = 'foo'

      id = Column(BigInteger, primary_key=True)

   class Bar(db.Model):
      __bind_key__ = 'bar'
      __tablename__ = 'bar'

      id = Column(BigInteger, primary_key=True)

The request handlers don't need to be modified and can continue working
normally. After this piece of configuration has been done, SQLAlchemy takes care
of routing the connection to the correct database according to what's being
queried.

For a complete example, please refer to `examples/multiple-databases.py`.

Migrations (using Alembic)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Database migrations are supported using Alembic_.

The one piece of configuration that Alembic expects to auto-generate migrations
is the |MetaData| object that your app is using. This is provided by the
:code:`db.metadata` property.

.. code-block:: python

   # env.py

   from tornado_sqlalchemy import SQLAlchemy

   db = SQLAlchemy(database_url)

   target_metadata = db.metadata

Other than that, the normal Alembic `configuration instructions`_ apply.

.. _alembic: http://alembic.sqlalchemy.org/en/latest/
.. _configuration instructions: https://alembic.sqlalchemy.org/en/latest/tutorial.html
.. _examples/basic.py: https://github.com/siddhantgoel/tornado-sqlalchemy/blob/main/examples/basic.py
.. _examples/multiple-databases.py: https://github.com/siddhantgoel/tornado-sqlalchemy/blob/main/examples/multiple-databases.py
.. _Future: http://www.tornadoweb.org/en/stable/concurrent.html#tornado.concurrent.Future
.. _MetaData: https://docs.sqlalchemy.org/en/13/core/metadata.html#sqlalchemy.schema.MetaData
.. |MetaData| replace:: ``MetaData``
.. _poorly suited for explicit asynchronous programming: https://stackoverflow.com/a/16503103/179729
.. _Query: http://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _standardized library: https://xkcd.com/927/
.. _tornado: https://www.tornadoweb.org/en/stable/
