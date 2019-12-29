from unittest import TestCase, mock
from sqlalchemy import Column, BigInteger, String

from ._common import db, User, mysql_url, mysql_url_2


db.Model2 = db.make_declarative_base()


class UserInBar(db.Model2):
    __bind_key__ = 'bar'
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(64), unique=True)

    def __init__(self, username):
        self.username = username


class MultipleBasesTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        super(MultipleBasesTestCase, self).setUp(*args, **kwargs)

        db.configure(uri=mysql_url, binds={'bar': mysql_url_2})

        self._application = mock.Mock()
        self._application.settings = {'db': db}

        db.create_all()
        db.Model2.metadata.create_all(db.get_engine('bar'))

    def tearDown(self, *args, **kwargs):
        db.drop_all()
        db.Model2.metadata.drop_all(db.get_engine('bar'))

        super(MultipleBasesTestCase, self).tearDown(*args, **kwargs)

    def test_multiple_bases(self):
        session = db.sessionmaker()

        session.add(User('a'))
        session.add(User('b'))
        session.commit()
        user_count_1 = session.query(User).count()

        session.add(UserInBar('a'))
        session.commit()

        user_in_bar_count = session.query(UserInBar).count()
        user_count_2 = session.query(User).count()

        session.close()

        self.assertEqual(user_count_1, 2)
        self.assertEqual(user_in_bar_count, 1)
        self.assertEqual(user_count_2, 2)
