from unittest import TestCase, mock
from sqlalchemy import Column, BigInteger, String

from ._common import db, User, mysql_url, mysql_url_1, mysql_url_2

class Foo(db.Model):
    __bind_key__ = 'foo'
    __tablename__ = 'foo'

    id = Column(BigInteger, primary_key=True)
    foo = Column(String(64))

    def __init__(self, foo):
        self.foo = foo


class MultiDatabasesTestCase(TestCase):

    def setUp(self, *args, **kwargs):
        super(MultiDatabasesTestCase, self).setUp(*args, **kwargs)

        self._application = mock.Mock()
        self._application.settings = {
            'sqlalchemy_database_uri': mysql_url,
            'sqlalchemy_binds': {
                'foo': mysql_url_1,
                'bar': mysql_url_2,
            }
        }
        db.init_app(self._application)
        db.create_all()

    def tearDown(self, *args, **kwargs):
        db.drop_all()

        super(MultiDatabasesTestCase, self).tearDown(*args, **kwargs)

    def test_add_objects(self):
        session = db.Session()
        user1 = User('a')
        user2 = User('a')

        session.add(user1)
        session.add(user2)
        user_count = session.query(User).count()

        foo = Foo('b')
        session.add(foo)
        foo_count = session.query(Foo).count()

        session.close()
        assert user_count == 2
        assert foo_count == 1