from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


async_pool = ThreadPoolExecutor(max_workers=5)


class MissingFactoryError(Exception):
    pass


def make_session_factory(database_url, pool_size, engine_events):
    engine = create_engine(database_url, pool_size=pool_size)

    for (name, listener) in engine_events:
        event.listen(engine, name, listener)

    factory = sessionmaker()
    factory.configure(bind=engine)

    return factory


def wrap_in_future(query):
    """Wrap a `sqlalchemy.orm.query.Query` object into a
    `concurrent.futures.Future` so that it can be yielded.

    :param query: `sqlalchemy.orm.query.Query` object
    :returns: `concurrent.futures.Future` object wrapping the given query so
    that tornado can yield on it.
    """
    return async_pool.submit(query)


class SessionMixin(object):
    @contextmanager
    def make_session(self):
        if not hasattr(self.application, 'session_factory'):
            raise MissingFactoryError()

        try:
            session = self.application.session_factory()

            yield session
        except:
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()
