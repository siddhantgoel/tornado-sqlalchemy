from tornado.gen import coroutine
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler


from ._common import BaseTestCase, User, mysql_url, db


from tornado_sqlalchemy import SessionMixin


class RequestHandlersTestCase(AsyncHTTPTestCase, BaseTestCase):
    def __init__(self, *args, **kwargs):
        super(RequestHandlersTestCase, self).__init__(*args, **kwargs)

        class SyncRequestHandler(SessionMixin, RequestHandler):
            def get(h_self):
                db.session.add(User('hunter2'))
                db.session.flush()
                count = User.count()
                h_self.write(str(count))

        class GenCoroutinesRequestHandler(SessionMixin, RequestHandler):
            @coroutine
            def get(h_self):
                count = yield User.count_gen_async()
                h_self.write(str(count))

        class NativeCoroutinesRequestHandler(SessionMixin, RequestHandler):
            async def get(h_self):
                count = await User.count_async()
                h_self.write(str(count))

        handlers = (
            (r'/sync', SyncRequestHandler),
            (r'/gen-coroutines', GenCoroutinesRequestHandler),
            (r'/native-coroutines', NativeCoroutinesRequestHandler),
        )

        db.configure(uri=mysql_url)

        self._application = Application(handlers, db=db)

    def get_app(self):
        return self._application

    def test_gen_coroutines(self):
        response = self.fetch('/gen-coroutines', method='GET')

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode('utf-8'), '0')

    def test_native_coroutines(self):
        response = self.fetch('/native-coroutines', method='GET')

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode('utf-8'), '0')

    def test_with_mixin(self):
        response = self.fetch('/sync', method='GET')

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode('utf-8'), '1')
