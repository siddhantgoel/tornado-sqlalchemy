tornado-sqlalchemy
==================

.. image:: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy.svg?branch=master
    :target: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy

.. image:: https://badge.fury.io/py/tornado-sqlalchemy.svg
    :target: https://pypi.python.org/pypi/tornado-sqlalchemy

**tornado-sqlalchemy** is a Python library aimed at providing a set of helpers
for using the SQLAlchemy_ database toolkit in tornado_ web applications.

Installation
------------

.. code-block:: bash

    $ pip install tornado-sqlalchemy

Background
----------

tornado_ is slightly different from the rest of the web frameworks, in that it
allows handling web requests asynchronously out of the box. At the same time,
making database operations asynchronous (especially when you put an ORM in the
picture) is not that straight forward.

Hence, the aim of this project is to provide a few helper functions which can
help you handle your database operations easily in case you're combining the two
libraries.

Before using this project, it's important to understand the main guideline this
project has - **We assume that the user knows how to use the two frameworks.**

Tornado is not like any other web framework, and to make use of the asynchronous
functions it provides, it's necessary to understand how it really behaves
underneath. In other words, you should **know** how that ioloop_ works.

Similarly, SQLAlchemy is an amazing framework, but I cannot stress how
important it is to understand how `session handling`_ works and how to work with
`connection and engine`_ objects.

We are not trying to add another layer of abstraction. The only thing we're
trying to do is provide a set of helper functions for applications that happen
to use both Tornado and SQLAlchemy.

Why?
----

.. role:: strike
    :class: strike

It seems like we should first answer the question - why does this library exist
in the first place? What problems/use-cases is it tackling?

- **Boilerplate** - Tornado does not bundle code to handle database connections.
  That's fine, because it's not in the business of writing database code anyway.
  Everyone ends up writing their own code. Code to establish database
  connections, initialize engines, get/teardown sessions, and so on.

- **Asynchronous query execution** - ORMs are `poorly suited for explicit
  asynchronous programming`_. You don't know what property access or what
  method call would end up hitting the database. For a situation like this, it's
  a good idea to decide on *what exactly* you want to execute in the background.

- **Database migrations** - Since you're using SQLAlchemy, you're probably also
  using alembic_ for database migrations. This again brings us to the point
  about boilerplate. If you're currently using SQLAlchemy with Tornado and have
  migrations setup using alembic, you likely have custom code written somewhere.

The intention here is to have answers to all three of these in a
`standardized library`_ which can act as a central place for all the
:strike:`bugs` features, and hopefully can establish best practices.

Usage
-----

Construct a :code:`session_factory` using :code:`make_session_factory` and pass
it to your :code:`Application` object.

.. code-block:: python

    >>> from tornado.web import Application
    >>> from tornado_sqlalchemy import make_session_factory
    >>>
    >>> factory = make_session_factory(database_url)
    >>> my_app = Application(handlers, session_factory=factory)

Add the :code:`SessionMixin` to your request handlers, which makes the
:code:`make_session` function available in the GET/POST/... methods you're
defining. And to run database queries in the background, use the
:code:`as_future` function to wrap the SQLAlchemy Query_ into a Future_ object,
which you can :code:`yield` on to get the result.

Since we're talking about :code:`yield`, please note that currently we don't
support the native :code:`asyncio.Future` objects included in Python 3. So if
your request handlers are :code:`async def`-ed, then calling :code:`await` on
the :code:`future` that :code:`as_future` returns would likely not work. But the
good news is that a later version of this library should support this use case
as well.

.. code-block:: python

    >>> from tornado.gen import coroutine
    >>> from tornado_sqlalchemy import SessionMixin, as_future
    >>>
    >>> class MyRequestHandler(RequestHandler, SessionMixin):
    >>>     @coroutine
    >>>     def get(self):
    >>>         with self.make_session() as session:
    >>>             count = yield as_future(session.query(User).count)
    >>>
    >>>         self.write('{} users so far!'.format(count))

To setup database migrations, make sure that your SQLAlchemy models are
inheriting using the result from the :code:`declarative_base` function provided.

.. code-block:: python

    >>> from sqlalchemy import Column, BigInteger, String
    >>> from tornado_sqlalchemy import declarative_base
    >>>
    >>> DeclarativeBase = declarative_base()
    >>>
    >>> class User(DeclarativeBase):
    >>>     id = Column(BigInteger, primary_key=True)
    >>>     username = Column(String(255), unique=True)

And use the same :code:`DeclarativeBase` object in the :code:`env.py` file that
alembic is using.

For a complete usage example, refer to the `examples/tornado_web.py`_.

.. _alembic: http://alembic.zzzcomputing.com/en/latest/
.. _connection and engine: http://docs.sqlalchemy.org/en/latest/core/connections.html
.. _declarative_base: http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/api.html#sqlalchemy.ext.declarative.declarative_base
.. _Future: https://docs.python.org/3/library/concurrent.futures.html#future-objects
.. _ioloop: http://www.tornadoweb.org/en/stable/ioloop.html
.. _Metadata: http://docs.sqlalchemy.org/en/latest/core/metadata.html#sqlalchemy.schema.MetaData
.. _poorly suited for explicit asynchronous programming: https://stackoverflow.com/a/16503103/179729
.. _Query: http://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query
.. _session handling: http://docs.sqlalchemy.org/en/latest/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it
.. _Session: http://docs.sqlalchemy.org/en/latest/orm/session_api.html#sqlalchemy.orm.session.Session
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _standardized library: https://xkcd.com/927/
.. _tornado: http://tornadoweb.org
.. _examples/tornado_web.py: https://github.com/siddhantgoel/tornado-sqlalchemy/blob/master/examples/tornado_web.py
