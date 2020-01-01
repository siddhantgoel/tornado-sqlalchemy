from unittest import TestCase, mock
from sqlalchemy import Column, BigInteger, String

from ._common import db, User, mysql_url, mysql_url_1, mysql_url_2


db.FooModel = db.make_declarative_base()

db.BarModel = db.make_declarative_base()


class FooUser(db.FooModel):
    __bind_key__ = 'foo'
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(64), unique=True)

    def __init__(self, username):
        self.username = username


class BarUser(db.BarModel):
    __bind_key__ = 'bar'
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(64), unique=True)

    def __init__(self, username):
        self.username = username


class MultipleBasesTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        super(MultipleBasesTestCase, self).setUp(*args, **kwargs)

        db.configure(
            uri=mysql_url, binds={'foo': mysql_url_1, 'bar': mysql_url_2}
        )

        self._application = mock.Mock()
        self._application.settings = {'db': db}

        db.create_all()
        db.FooModel.metadata.create_all(db.get_engine('foo'))
        db.BarModel.metadata.create_all(db.get_engine('bar'))

    def tearDown(self, *args, **kwargs):
        db.drop_all()
        db.FooModel.metadata.drop_all(db.get_engine('foo'))
        db.BarModel.metadata.drop_all(db.get_engine('bar'))

        super(MultipleBasesTestCase, self).tearDown(*args, **kwargs)

    def test_multiple_bases(self):
        session = db.sessionmaker()

        session.add(User('first'))
        session.commit()

        session.add(FooUser('first'))
        session.add(FooUser('second'))
        session.commit()

        session.add(BarUser('first'))
        session.add(BarUser('second'))
        session.add(BarUser('third'))
        session.commit()

        user_count = session.query(User).count()
        foo_user_count = session.query(FooUser).count()
        bar_user_count = session.query(BarUser).count()

        session.close()

        self.assertEqual(user_count, 1)
        self.assertEqual(foo_user_count, 2)
        self.assertEqual(bar_user_count, 3)
