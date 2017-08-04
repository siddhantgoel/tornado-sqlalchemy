==================
tornado-sqlalchemy
==================

.. image:: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy.svg?branch=master
    :target: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy

.. image:: https://badge.fury.io/py/tornado-sqlalchemy.svg
    :target: https://pypi.python.org/pypi/tornado-sqlalchemy

**tornado-sqlalchemy** is a Python library aimed at simplifying the use of
SQLAlchemy_ database toolkit in the context of the tornado_ web framework.

Installation
============

.. code-block:: bash

    $ pip install streaming_form_data

Background
==========

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
underneath. In other words, you should **know** how `ioloop`_ works.

Similarly, SQLAlchemy is an amazing framework, but I cannot stress how
important it is to understand how `session handling`_ works and how to work with
`connection and engine`_ objects.

We are not trying to add another layer of abstraction. The only thing we're
trying to do is provide a set of helper functions for applications that happen
to use both Tornado and SQLAlchemy.

Why?
====

.. role:: strike
    :class: strike

It seems like we should first answer the question - why does this library exist
in the first place? What problems/use-cases is it tackling?

- **Boilerplate** - Tornado does not bundle code to handle database connections.
  That's fine, because it's not in the business of making database code anyway.
  Everyone ends up writing their own code. Code to establish database
  connections, initialize engines, get/teardown sessions, and so on.

- **Asynchronous query execution** - ORMs are `poorly suited for explicit
  asynchronous programming`_. You don't know what property access or what
  method call would end up hitting the database. For a situation like this, it's
  a good idea to decide on *what exactly* you want to execute in the background.

- **Database migrations** - Since you're using SQLAlchemy, you're probably also
  using alembic_ for database migrations. This again brings us to the point
  about Boilerplate. If you're currently using SQLAlchemy with Tornado and have
  migrations setup using alembic, you likely have custom code written somewhere.

The intention here is to have answers to all three of these in a
`standardized library`_ which can act as a central place for all the
:strike:`bugs` features, and hopefully can establish best practices.

.. _alembic: http://alembic.zzzcomputing.com/en/latest/
.. _connection and engine: http://docs.sqlalchemy.org/en/latest/core/connections.html
.. _declarative_base: http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/api.html#sqlalchemy.ext.declarative.declarative_base
.. _ioloop: http://www.tornadoweb.org/en/stable/ioloop.html
.. _Metadata: http://docs.sqlalchemy.org/en/latest/core/metadata.html#sqlalchemy.schema.MetaData
.. _poorly suited for explicit asynchronous programming: https://stackoverflow.com/a/16503103/179729
.. _Query: http://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query
.. _session handling: http://docs.sqlalchemy.org/en/latest/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it
.. _Session: http://docs.sqlalchemy.org/en/latest/orm/session_api.html#sqlalchemy.orm.session.Session
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _standardized library: https://xkcd.com/927/
.. _tornado: http://tornadoweb.org
