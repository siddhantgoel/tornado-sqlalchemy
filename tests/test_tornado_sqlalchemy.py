from unittest import TestCase

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from sqlalchemy import Column, BigInteger, String
from tornado_sqlalchemy import (declarative_base, MissingFactoryError,
                                SessionFactory, SessionMixin)


database_url = 'postgres://postgres:@localhost/tornado_sqlalchemy'


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), unique=True)

    def __init__(self, username):
        self.username = username


class BaseTestCase(TestCase):
    def setUp(self):
        self.factory = SessionFactory(database_url)

        Base.metadata.create_all(self.factory.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.factory.engine)


class SessionFactoryTestCase(BaseTestCase):
    def test_make_session(self):
        session = self.factory.make_session()

        self.assertTrue(session)
        self.assertEqual(session.query(User).count(), 0)

        session.close()


class SessionMixinTestCase(BaseTestCase):
    def test_mixin_ok(self):
        class GoodHandler(SessionMixin):
            def __init__(h_self):
                h_self.application = Mock()
                h_self.application.session_factory = self.factory

            def run(h_self):
                with h_self.make_session() as session:
                    return session.query(User).count()

        self.assertEqual(GoodHandler().run(), 0)

    def test_mixin_no_session_factory(self):
        class BadHandler(SessionMixin):
            def __init__(h_self):
                h_self.application = None

            def run(h_self):
                with h_self.make_session() as session:
                    return session.query(User).count()

        self.assertRaises(MissingFactoryError, BadHandler().run)
