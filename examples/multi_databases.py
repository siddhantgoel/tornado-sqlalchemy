from sqlalchemy import BigInteger, Column, String
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from tornado_sqlalchemy import (
    SessionMixin,
    as_future,
    set_max_workers,
    SQLAlchemy,
)


db = SQLAlchemy()

set_max_workers(10)


class User(db.Model):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(255))


class Foo(db.Model):
    __bind_key__ = 'foo'
    __tablename__ = 'foo'

    id = Column(BigInteger, primary_key=True)
    foo = Column(String(255))


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
            session.add(User(username='b'))
            session.add(Foo(foo='foo'))
            session.commit()
            count = yield as_future(session.query(User).count)

        self.write('{} users so far!'.format(count))


class NativeCoroutinesRequestHandler(SessionMixin, RequestHandler):
    async def get(self):
        with self.make_session() as session:
            session.add(User(username='c'))
            session.add(Foo(foo='d'))
            session.commit()
            count = await as_future(session.query(User).count)

        self.write('{} users so far!'.format(count))


if __name__ == '__main__':
    db.configure(
        uri='mysql://t_sa:t_sa@localhost/t_sa',
        binds={
            'foo': 'mysql://t_sa:t_sa@localhost/t_sa_1',
            'bar': 'mysql://t_sa:t_sa@localhost/t_sa_2',
        },
        engine_options={
            'pool_size': 10,
            'pool_timeout': 0,
            'max_overflow': -1,
        },
    )

    app = Application(
        [
            (r'/sync', SynchronousRequestHandler),
            (r'/gen-coroutines', GenCoroutinesRequestHandler),
            (r'/native-coroutines', NativeCoroutinesRequestHandler),
        ],
        db=db,
        autoreload=True,
    )

    db.create_all()

    session = db.sessionmaker()
    session.add(User(username='a'))
    session.commit()
    session.close()

    print('Listening on port 8888')

    app.listen(8888)
    IOLoop.current().start()
