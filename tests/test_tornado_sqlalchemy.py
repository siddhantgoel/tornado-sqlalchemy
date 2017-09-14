from unittest import TestCase

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from sqlalchemy import Column, BigInteger, String
from tornado_sqlalchemy import (
    as_future, declarative_base, MissingFactoryError, make_session_factory,
    SessionMixin)
from tornado.gen import coroutine
from tornado.web import Application, RequestHandler
from tornado.testing import AsyncHTTPTestCase

database_url = 'postgres://postgres:@localhost/tornado_sqlalchemy'
mysql_url = 'mysql://mysql_user:mysql_pass@localhost/tornado_sqlalchemy'

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), unique=True)

    def __init__(self, username):
        self.username = username


class BaseTestCase(TestCase):
    def setUp(self):
        self.factory = make_session_factory(database_url)

        Base.metadata.create_all(self.factory.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.factory.engine)


class FactoryTestCase(TestCase):
    def test_make_mysql_factoy(self):
        factory = make_session_factory(mysql_url)

        self.assertTrue(factory)

    def test_make_postgres_factory(self):
        factory = make_session_factory(database_url)

        self.assertTrue(factory)


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
                h_self.application.settings = {'session_factory': self.factory}

            def run(h_self):
                with h_self.make_session() as session:
                    return session.query(User).count()

        self.assertEqual(GoodHandler().run(), 0)

    def test_mixin_no_session_factory(self):
        class BadHandler(SessionMixin):
            def __init__(h_self):
                h_self.application = Mock()
                h_self.application.settings = {}

            def run(h_self):
                with h_self.make_session() as session:
                    return session.query(User).count()

        self.assertRaises(MissingFactoryError, BadHandler().run)


class RequestHandlersTestCase(AsyncHTTPTestCase):
    def __init__(self, *args, **kwargs):
        super(RequestHandlersTestCase, self).__init__(*args, **kwargs)

        class WithoutMixinRequestHandler(RequestHandler):
            def get(h_self):
                with h_self.make_session() as session:
                    count = session.query(User).count()

                h_self.write(str(count))

        class WithMixinRequestHandler(RequestHandler, SessionMixin):
            def get(h_self):
                with h_self.make_session() as session:
                    count = session.query(User).count()

                h_self.write(str(count))

        class AsyncRequestHandler(RequestHandler, SessionMixin):
            @coroutine
            def get(h_self):
                with h_self.make_session() as session:
                    count = yield as_future(session.query(User).count)

                h_self.write(str(count))

        handlers = (
            (r'/async', AsyncRequestHandler),
            (r'/with-mixin', WithMixinRequestHandler),
            (r'/without-mixin', WithoutMixinRequestHandler),
        )

        self._factory = make_session_factory(database_url)
        self._application = Application(
            handlers, session_factory=self._factory)

    def setUp(self, *args, **kwargs):
        super(RequestHandlersTestCase, self).setUp(*args, **kwargs)

        Base.metadata.create_all(self._factory.engine)

    def tearDown(self, *args, **kwargs):
        Base.metadata.drop_all(self._factory.engine)

        super(RequestHandlersTestCase, self).tearDown(*args, **kwargs)

    def get_app(self):
        return self._application

    def test_async(self):
        response = self.fetch('/async', method='GET')

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode('utf-8'), '0')

    def test_with_mixin(self):
        response = self.fetch('/with-mixin', method='GET')

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode('utf-8'), '0')

    def test_without_mixin(self):
        response = self.fetch('/without-mixin', method='GET')
        self.assertEqual(response.code, 500)
