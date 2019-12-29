from unittest import TestCase, mock
from sqlalchemy import Column, BigInteger, String

from ._common import db, mysql_url, mysql_url_1, mysql_url_2


class Foo(db.Model):
    __bind_key__ = 'foo'
    __tablename__ = 'foo'

    id = Column(BigInteger, primary_key=True)
    foo = Column(String(64))

    def __init__(self, foo):
        self.foo = foo


class Bar(db.Model):
    __bind_key__ = 'bar'
    __tablename__ = 'bar'

    id = Column(BigInteger, primary_key=True)
    bar = Column(String(64))

    def __init__(self, bar):
        self.bar = bar


class MultiDatabasesTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        super(MultiDatabasesTestCase, self).setUp(*args, **kwargs)

        db.configure(
            uri=mysql_url, binds={'foo': mysql_url_1, 'bar': mysql_url_2}
        )

        self._application = mock.Mock()
        self._application.settings = {'db': db}

        db.create_all()

    def tearDown(self, *args, **kwargs):
        db.drop_all()
        super(MultiDatabasesTestCase, self).tearDown(*args, **kwargs)

    def test_add_objects(self):
        session = db.sessionmaker()

        session.add(Foo('foo'))
        session.commit()
        foo_count = (
            db.get_engine('foo')
            .execute("SELECT COUNT(*) FROM foo")
            .fetchone()[0]
        )

        session.add(Bar('first bar'))
        session.add(Bar('second bar'))
        session.commit()
        bar_count = (
            db.get_engine('bar')
            .execute("SELECT COUNT(*) FROM bar")
            .fetchone()[0]
        )
        session.close()

        assert foo_count == 1
        assert bar_count == 2
