from sqlalchemy import BigInteger, Column, String
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import Application, RequestHandler

from tornado_sqlalchemy import SessionMixin, as_future, SQLAlchemy


db = SQLAlchemy()


define('database-url', type=str, help='Database URL')


class User(db.Model):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), unique=True)


class SynchronousRequestHandler(SessionMixin, RequestHandler):
    def get(self):
        with self.make_session() as session:
            count = session.query(User).count()

        # OR count = self.session.query(User).count()

        self.write('{} users so far!'.format(count))


class GenCoroutinesRequestHandler(SessionMixin, RequestHandler):
    @coroutine
    def get(self):
        with self.make_session() as session:
            count = yield as_future(session.query(User).count)

        self.write('{} users so far!'.format(count))


class NativeCoroutinesRequestHandler(SessionMixin, RequestHandler):
    async def get(self):
        with self.make_session() as session:
            count = await as_future(session.query(User).count)

        self.write('{} users so far!'.format(count))


if __name__ == '__main__':
    parse_command_line()

    assert options.database_url, "Need a database URL"

    db.configure(uri=options.database_url)

    app = Application(
        [
            (r'/sync', SynchronousRequestHandler),
            (r'/gen-coroutines', GenCoroutinesRequestHandler),
            (r'/native-coroutines', NativeCoroutinesRequestHandler),
        ],
        db=db,
    )

    app.listen(8888)
    print('Listening on port 8888')

    IOLoop.current().start()
