tornado-sqlalchemy
==================

.. image:: https://badge.fury.io/py/tornado-sqlalchemy.svg
    :target: https://pypi.python.org/pypi/tornado-sqlalchemy

.. image:: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy.svg?branch=master
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

    >>> from tornado.gen import coroutine
    >>> from tornado.web import Application, RequestHandler
    >>> from tornado_sqlalchemy import as_future, make_session_factory, SessionMixin
    >>>
    >>> factory = make_session_factory('postgres://user:password@host/database')
    >>>
    >>> class MyRequestHandler(RequestHandler, SessionMixin):
    ...     @coroutine
    ...     def get(self):
    ...         with self.make_session() as session:
    ...             count = yield as_future(session.query(UserModel).count)
    ...
    ...         self.write('{} users so far!'.format(count)
    ...
    >>> app = Application(((r'/', MyRequestHandler),), session_factory=factory)

Documentation
-------------

Documentation is available at `Read The Docs`_.

.. _Read The Docs: https://tornado-sqlalchemy.readthedocs.io
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _tornado: http://tornadoweb.org
