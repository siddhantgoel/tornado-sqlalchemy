from http import HTTPStatus

from tornado.gen import coroutine
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from tornado_sqlalchemy import SessionMixin, as_future

from ._common import BaseTestCase, User, mysql_url, db


class RequestHandlersTestCase(AsyncHTTPTestCase, BaseTestCase):
    def __init__(self, *args, **kwargs):
        super(RequestHandlersTestCase, self).__init__(*args, **kwargs)

        class WithoutMixinRequestHandler(RequestHandler):
            def get(h_self):
                with h_self.make_session() as session:
                    count = session.query(User).count()

                h_self.write(str(count))

        class WithMixinRequestHandler(SessionMixin, RequestHandler):
            def get(h_self):
                with h_self.make_session() as session:
                    session.add(User('hunter2'))
                    session.flush()

                    count = session.query(User).count()

                h_self.write(str(count))

        class GenCoroutinesRequestHandler(SessionMixin, RequestHandler):
            @coroutine
            def get(h_self):
                with h_self.make_session() as session:
                    count = yield as_future(session.query(User).count)

                h_self.write(str(count))

        class NativeCoroutinesRequestHandler(SessionMixin, RequestHandler):
            async def get(h_self):
                with h_self.make_session() as session:
                    count = await as_future(session.query(User).count)

                h_self.write(str(count))

        class UsesSelfSessionRequestHandler(SessionMixin, RequestHandler):
            def get(h_self):
                h_self.write(str(h_self.session.query(User).count()))

        handlers = (
            (r'/gen-coroutines', GenCoroutinesRequestHandler),
            (r'/native-coroutines', NativeCoroutinesRequestHandler),
            (r'/uses-self-session', UsesSelfSessionRequestHandler),
            (r'/with-mixin', WithMixinRequestHandler),
            (r'/without-mixin', WithoutMixinRequestHandler),
        )

        db.configure(url=mysql_url)

        self._application = Application(handlers, db=db)

    def get_app(self):
        return self._application

    def test_gen_coroutines(self):
        response = self.fetch('/gen-coroutines', method='GET')

        self.assertEqual(response.code, HTTPStatus.OK.value)
        self.assertEqual(response.body.decode('utf-8'), '0')

    def test_native_coroutines(self):
        response = self.fetch('/native-coroutines', method='GET')

        self.assertEqual(response.code, HTTPStatus.OK.value)
        self.assertEqual(response.body.decode('utf-8'), '0')

    def test_with_mixin(self):
        response = self.fetch('/with-mixin', method='GET')

        self.assertEqual(response.code, HTTPStatus.OK.value)
        self.assertEqual(response.body.decode('utf-8'), '1')

    def test_without_mixin(self):
        response = self.fetch('/without-mixin', method='GET')

        self.assertEqual(response.code, HTTPStatus.INTERNAL_SERVER_ERROR.value)

    def test_uses_self_session(self):
        response = self.fetch('/uses-self-session', method='GET')

        self.assertEqual(response.code, HTTPStatus.OK.value)
        self.assertEqual(response.body.decode('utf-8'), '0')
