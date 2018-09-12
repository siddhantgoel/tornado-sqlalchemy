from sqlalchemy import Column, BigInteger, String
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado_sqlalchemy import (as_future, declarative_base,
                                make_session_factory, SessionMixin)
from tornado.web import RequestHandler, Application


DeclarativeBase = declarative_base()


class User(DeclarativeBase):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), unique=True)


class SyncWebRequestHandler(SessionMixin, RequestHandler):
    def get(self):
        with self.make_session() as session:
            count = session.query(User).count()

        self.write('{} users so far!'.format(count))


class AsyncWebRequestHandler(SessionMixin, RequestHandler):
    @coroutine
    def get(self):
        with self.make_session() as session:
            count = yield as_future(session.query(User).count)

        self.write('{} users so far!'.format(count))


class UsesSelfSessionRequestHandler(SessionMixin, RequestHandler):
    @coroutine
    def get(self):
        count = self.session.query(User).count()

        self.write('{} users so far!'.format(count))


if __name__ == '__main__':
    session_factory = make_session_factory(options.database_url)

    Application([
        (r'/sync', SyncWebRequestHandler)
        (r'/async', AsyncWebRequestHandler)
        (r'/uses-self-session', UsesSelfSessionRequestHandler)
    ], session_factory=session_factory).listen(8888)

    IOLoop.current().start()
