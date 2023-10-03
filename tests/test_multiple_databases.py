from http import HTTPStatus
from unittest import TestCase, mock

from sqlalchemy import Column, BigInteger, String, text

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from tornado_sqlalchemy import SessionMixin

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


class MultipleDatabasesTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        super(MultipleDatabasesTestCase, self).setUp(*args, **kwargs)

        db.configure(
            url=mysql_url, binds={'foo': mysql_url_1, 'bar': mysql_url_2}
        )

        self._application = mock.Mock()
        self._application.settings = {'db': db}

        db.create_all()

    def tearDown(self, *args, **kwargs):
        db.drop_all()

        super(MultipleDatabasesTestCase, self).tearDown(*args, **kwargs)

    def test_add_objects(self):
        session = db.sessionmaker()

        session.add(Foo('foo'))
        session.commit()

        session.add(Bar('first bar'))
        session.add(Bar('second bar'))
        session.commit()

        with db.get_engine('foo').begin() as conn:
            foo_count = conn.execute(text("SELECT COUNT(*) FROM foo")).fetchone()[0]

        with db.get_engine('bar').begin() as conn:
            bar_count = conn.execute(text("SELECT COUNT(*) FROM bar")).fetchone()[0]

        session.close()

        self.assertEqual(foo_count, 1)
        self.assertEqual(bar_count, 2)


class RequestHandlersTestCase(AsyncHTTPTestCase, TestCase):
    def __init__(self, *args, **kwargs):
        super(RequestHandlersTestCase, self).__init__(*args, **kwargs)

        db.configure(
            url=mysql_url, binds={'foo': mysql_url_1, 'bar': mysql_url_2}
        )

        class IndexRequestHandler(SessionMixin, RequestHandler):
            def get(h_self):
                with h_self.make_session() as session:
                    session.add(Foo('first-foo'))

                    session.add(Bar('first-bar'))
                    session.add(Bar('second-bar'))

                    session.flush()

                    foo_count = session.query(Foo).count()
                    bar_count = session.query(Bar).count()

                h_self.write('{}, {}'.format(foo_count, bar_count))

        handlers = ((r'/', IndexRequestHandler),)

        self._application = Application(handlers, db=db)

    def setUp(self, *args, **kwargs):
        super(RequestHandlersTestCase, self).setUp(*args, **kwargs)

        db.create_all()

    def tearDown(self, *args, **kwargs):
        db.drop_all()

        super(RequestHandlersTestCase, self).tearDown(*args, **kwargs)

    def get_app(self):
        return self._application

    def test_count(self):
        response = self.fetch('/', method='GET')

        self.assertEqual(response.code, HTTPStatus.OK.value)
        self.assertEqual(response.body.decode('utf-8'), '1, 2')
