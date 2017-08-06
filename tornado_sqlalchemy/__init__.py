from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base as _declarative_base
from sqlalchemy.orm import sessionmaker


__all__ = ['SessionMixin', 'set_max_workers', 'wrap_in_future',
           'make_session_factory', 'declarative_base']


class MissingFactoryError(Exception):
    pass


class AsyncExecution(object):
    _default_max_workers = 5

    def __init__(self, max_workers=None):
        self._max_workers = max_workers or self._default_max_workers
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    def set_max_workers(self, count):
        if self._pool:
            self._pool.shutdown(wait=True)

        self._max_workers = count
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    def wrap_in_future(self, query):
        """Wrap a `sqlalchemy.orm.query.Query` object into a
        `concurrent.futures.Future` so that it can be yielded.

        :param query: `sqlalchemy.orm.query.Query` object
        :returns: `concurrent.futures.Future` object wrapping the given query
        so that tornado can yield on it.
        """
        return self._pool.submit(query)


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
            raise
        else:
            session.commit()
        finally:
            session.close()


_async_exec = AsyncExecution()

set_max_workers = _async_exec.set_max_workers

wrap_in_future = _async_exec.wrap_in_future


def make_session_factory(database_url, pool_size, engine_events=None):
    engine = create_engine(database_url, pool_size=pool_size)

    if engine_events:
        for (name, listener) in engine_events:
            event.listen(engine, name, listener)

    factory = sessionmaker()
    factory.configure(bind=engine)

    return factory


def declarative_base():
    if not declarative_base._instance:
        declarative_base._instance = _declarative_base()
    return declarative_base._instance
