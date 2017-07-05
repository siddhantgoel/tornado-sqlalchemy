from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado_sqlalchemy import (make_session_factory, SessionMixin,
                                wrap_in_future)
from tornado.web import RequestHandler, Application

from app.models.user import User


def do_something(session):
    pass


class SyncWebRequestHandler(RequestHandler, SessionMixin):
    def get(self):
        with self.make_session() as session:
            do_something(session)

        self.write('Done!')


class AsyncWebRequestHandler(RequestHandler, SessionMixin):
    @coroutine
    def get(self):
        with self.make_session() as session:
            results = yield wrap_in_future(session.query(User).all)

            do_something(results)

        self.write('Done!')


if __name__ == '__main__':
    session_factory = make_session_factory(options.database_url)

    Application([
        (r'/sync', SyncWebRequestHandler)
        (r'/async', AsyncWebRequestHandler)
    ], session_factory=session_factory).listen(8888)

    IOLoop.current().start()
