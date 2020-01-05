Upgrading
=========

0.6 -> 0.7
----------

:code:`0.7` now **requires** a global :code:`SQLAlchemy` object, like the
following.

.. code-block:: python
   from tornado_sqlalchemy import SQLAlchemy

   db = SQLAlchemy(database_url='postgres://user:pass@host/database')

There should be only one of this, ideally in the main application file where
you're initializing your :code:`tornado.web.Application` object.

Once that is in place, the following changes are required.

1. Replace the :code:`session_factory` argument with the newly constructed
   :code:`SQLAlchemy` instance.

.. code-block:: python

   from tornado.web import Application
   from tornado_sqlalchemy import SQLAlchemy

   from my_app.handlers import IndexHandler

   db = SQLAlchemy(database_url='postgres://user:pass@host/database')

   app = Application(((r'/', IndexHandler),), db=db)

2. Make sure that your database models inherit from :code:`db.Model`.

.. code-block:: python

   from sqlalchemy import BigInteger, Column, String

   db = SQLAlchemy(database_url='postgres://user:pass@host/database')

   class User(db.Model):
       __tablename__ = 'users'

       id = Column(BigInteger, primary_key=True)
       username = Column(String(255), unique=True)

That should basically be it. If not, please `file an issue`_.

.. _file an issue: https://github.com/siddhantgoel/tornado-sqlalchemy/issues
