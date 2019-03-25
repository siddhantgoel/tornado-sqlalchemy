import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base as sa_declarative_base
from sqlalchemy.orm import sessionmaker
from tornado.concurrent import Future, chain_future
from tornado.ioloop import IOLoop

__all__ = (
    'as_future',
    'declarative_base',
    'make_session_factory',
    'SessionMixin',
    'set_max_workers',
)


class MissingFactoryError(Exception):
    pass


class _AsyncExecution:
    """Tiny wrapper around ThreadPoolExecutor. This class is not meant to be
    instantiated externally, but internally we just use it as a wrapper around
    ThreadPoolExecutor so we can control the pool size and make the
    `as_future` function public.

    Parameters
    ----------
    max_workers : int
        Worker count for the ThreadPoolExecutor
    """

    def __init__(self, max_workers=None):
        self._max_workers = max_workers or multiprocessing.cpu_count()
        self._pool = None

    def set_max_workers(self, count):
        if self._pool:
            self._pool.shutdown(wait=True)

        self._max_workers = count
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    def as_future(self, query):
        """Wrap a `sqlalchemy.orm.query.Query` object into a
        `concurrent.futures.Future` so that it can be yielded.

        Parameters
        ----------
        query : sqlalchemy.orm.query.Query
            SQLAlchemy query object to execute

        Returns
        -------
            tornado.concurrent.Future
                A `Future` object wrapping the given query so that tornado can
                await/yield on it
        """
        # concurrent.futures.Future is not compatible with the "new style"
        # asyncio Future, and awaiting on such "old-style" futures does not
        # work.
        #
        # tornado includes a `run_in_executor` function to help with this
        # problem, but it's only included in version 5+. Hence, we copy a
        # little bit of code here to handle this incompatibility.

        if not self._pool:
            self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

        old_future = self._pool.submit(query)
        new_future = Future()

        IOLoop.current().add_future(
            old_future, lambda f: chain_future(f, new_future)
        )

        return new_future


class SessionFactory:
    """SessionFactory is a wrapper around the functions that SQLAlchemy
    provides. The intention here is to let the user work at the session level
    instead of engines and connections.
    """

    def __init__(self, *args, **kwargs):
        self._engine = create_engine(*args, **kwargs)

        self._factory = sessionmaker()
        self._factory.configure(bind=self._engine)

    def make_session(self):
        return self._factory()

    @property
    def engine(self):
        return self._engine


class SessionMixin:
    _session = None

    @contextmanager
    def make_session(self):
        session = None

        try:
            session = self._make_session()

            yield session
        except Exception:
            if session:
                session.rollback()
            raise
        else:
            session.commit()
        finally:
            if session:
                session.close()

    def on_finish(self):
        next_on_finish = None

        try:
            next_on_finish = super(SessionMixin, self).on_finish
        except AttributeError:
            pass

        if self._session:
            self._session.commit()
            self._session.close()

        if next_on_finish:
            next_on_finish()

    @property
    def session(self):
        if not self._session:
            self._session = self._make_session()
        return self._session

    def _make_session(self):
        factory = self.application.settings.get('session_factory')

        if not factory:
            raise MissingFactoryError()

        return factory.make_session()


_async_exec = _AsyncExecution()

as_future = _async_exec.as_future

set_max_workers = _async_exec.set_max_workers


def make_session_factory(*args, **kwargs):
    return SessionFactory(*args, **kwargs)


class _declarative_base:
    def __init__(self):
        self._instance = None

    def __call__(self):
        if not self._instance:
            self._instance = sa_declarative_base()
        return self._instance


declarative_base = _declarative_base()
