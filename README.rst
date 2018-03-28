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
    >>> class MyRequestHandler(SessionMixin, RequestHandler):
    ...     @coroutine
    ...     def get(self):
    ...         with self.make_session() as session:
    ...             count = yield as_future(session.query(UserModel).count)
    ...
    ...         # OR count = self.session.query(UserModel).count()
    ...
    ...         self.write('{} users so far!'.format(count))
    ...
    >>> app = Application(((r'/', MyRequestHandler),), session_factory=factory)

Documentation
-------------

Documentation is available at `Read The Docs`_.


Development
-----------

To work on this package, please make sure you have a working Python
installation on your system.

1. Create a virtualenv -
   :code:`python -m venv venv && source venv/bin/activate`.

2. Git clone the repository -
   :code:`git clone https://github.com/siddhantgoel/tornado-sqlalchemy`

3. Install the packages required for development -
   :code:`pip install -r requirements.txt`

4. Install this package - :code:`pip install .`.

5. You should now be able to run the test suite - :code:`py.test tests/`.

.. _Read The Docs: https://tornado-sqlalchemy.readthedocs.io
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _tornado: http://tornadoweb.org
