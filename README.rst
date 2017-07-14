tornado-sqlalchemy
==================

.. image:: https://badge.fury.io/py/tornado-sqlalchemy.svg
    :target: https://pypi.python.org/pypi/tornado-sqlalchemy

.. image:: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy.svg?branch=master
    :target: https://travis-ci.org/siddhantgoel/tornado-sqlalchemy

`tornado-sqlalchemy` is a Python library aimed at integrating the tornado_ web
framework and the SQLAlchemy_ database toolkit.

tornado_ is slightly different from the rest of the web frameworks, in that it
allows handling web requests asynchronously out of the box. At the same time,
making database operations asynchronous (especially when you put an ORM in the
picture) is not that straight forward. Hence, the aim of this project is to
provide a few helper functions which can help you handle your database
operations easily in case you're combining the two libraries.

This is not an end-to-end solution for your database needs, but rather it
assumes that the developer knows what they're doing, how the two libraries work,
and especially how `session handling`_ in SQLAlchemy_ works.

This project is under heavy development, and makes no promises until the API
stabilizes. You have been warned!

.. _tornado: http://tornadoweb.org
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _alembic: http://alembic.zzzcomputing.com/en/latest/
.. _session handling: http://docs.sqlalchemy.org/en/latest/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it
.. _entry points: http://www.tornadoweb.org/en/stable/web.html#entry-points
.. _tornado Application: 
