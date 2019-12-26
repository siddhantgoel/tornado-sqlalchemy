import asyncio
import contextvars

from typing import *
from sqlalchemy import BigInteger, Column, String
from tornado.gen import coroutine, sleep
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from tests._common import mysql_url

from tornado_sqlalchemy import (
    SessionMixin,
    as_future,
    SQLAlchemy,
)

db = SQLAlchemy()

RequestId = contextvars.ContextVar('request_id')

class User(db.Model):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), unique=True)


class RequestIdMixin(object):

    def prepare(self) -> Optional[Awaitable[None]]:

        self.request_id = id(self.request)
        RequestId.set(self.request_id)

        print('----prepare id: ', self.request_id, RequestId.get())

    def on_finish(self):
        print('-----finish id: ', self.request_id, RequestId.get())

    def func(self):
        print('func id:', self.request_id, RequestId.get())
        assert self.request_id == RequestId.get()

    @coroutine
    def coroutine_func(self):
        print('coroutine_func id:', self.request_id, RequestId.get())
        assert self.request_id == RequestId.get()

    async def async_func(self):
        print('async_func id:', self.request_id, RequestId.get())
        assert self.request_id == RequestId.get()


class SynchronousRequestHandler(SessionMixin, RequestIdMixin, RequestHandler):

    def get(self):
        with self.make_session() as session:
            count = session.query(User).count()

        # OR count = self.session.query(User).count()

        self.func()
        self.write('{} users so far!'.format(count))


class GenCoroutinesRequestHandler(SessionMixin, RequestIdMixin, RequestHandler):
    @coroutine
    def get(self):
        with self.make_session() as session:
            count = yield as_future(session.query(User).count)

        yield self.coroutine_func()
        yield sleep(5)
        yield self.coroutine_func()

        self.write('{} users so far!'.format(count))


class NativeCoroutinesRequestHandler(SessionMixin, RequestIdMixin, RequestHandler):
    async def get(self):
        # with self.make_session() as session:
        #     count = await as_future(session.query(User).count)

        await self.async_func()
        await asyncio.sleep(5)
        await self.async_func()

        self.write('{} users so far!'.format(0))


if __name__ == '__main__':

    app = Application(
        [
            (r'/sync', SynchronousRequestHandler),
            (r'/gen-coroutines', GenCoroutinesRequestHandler),
            (r'/native-coroutines', NativeCoroutinesRequestHandler),
        ],
        sqlalchemy_database_uri=mysql_url,
        autoreload=True
    )

    db.init_app(app)
    db.create_all()

    app.listen(8888)
    print('Listening on port 8888')

    IOLoop.current().start()
