## Upgrading

## 0.6 -> 0.7

`0.7` now **requires** a global `SQLAlchemy` object, like the following.

```python
from tornado_sqlalchemy import SQLAlchemy

db = SQLAlchemy(database_url='postgres://user:pass@host/database')
```

There should be only one of this, ideally in the main application file where
you're initializing your `tornado.web.Application` object.

Once that is in place, the following changes are required.

1. Replace the `session_factory` argument with the newly constructed
   `SQLAlchemy` instance.

   ```python
   from tornado.web import Application
   from tornado_sqlalchemy import SQLAlchemy

   from my_app.handlers import IndexHandler

   db = SQLAlchemy(database_url='postgres://user:pass@host/database')

   app = Application(((r'/', IndexHandler),), db=db)
   ```
2. Make sure that your database models inherit from `db.Model`.

   ```python
   from sqlalchemy import BigInteger, Column, String

   db = SQLAlchemy(database_url='postgres://user:pass@host/database')

   class User(db.Model):
       __tablename__ = 'users'

       id = Column(BigInteger, primary_key=True)
       username = Column(String(255), unique=True)
    ```

That should be it. If not, please [file an issue].

[file an issue]: https://github.com/siddhantgoel/tornado-sqlalchemy/issues
