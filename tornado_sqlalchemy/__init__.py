import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base as sa_declarative_base
from sqlalchemy.orm import sessionmaker
from tornado.concurrent import Future, chain_future
from tornado.ioloop import IOLoop


__all__ = ['SessionMixin', 'set_max_workers', 'as_future',
           'make_session_factory', 'declarative_base']


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

        IOLoop.current().add_future(old_future,
                                    lambda f: chain_future(f, new_future))

        return new_future


class SessionFactory:
    """SessionFactory is a wrapper around the functions that SQLAlchemy
    provides. The intention here is to let the user work at the session level
    instead of engines and connections.

    Parameters
    ----------
        database_url : str
            Database URL
        pool_size : int
            Connection pool size
        use_native_unicode : bool
            Enable/disable native unicode support; this is only used in case
            the driver is psycopg2
        engine_events : List[Tuple[str, Callable]]
            List of (name, listener_function) tuples to subscribe to engine
            events
        session_events : List[Tuple[str, Callable]]
            List of (name, listener_function) tuples to subscribe to session
            events
    """

    def __init__(self, database_url, pool_size=None, use_native_unicode=True,
                 engine_events=None, session_events=None):
        self._database_url = make_url(database_url)
        self._pool_size = pool_size
        self._engine_events = engine_events
        self._session_events = session_events
        self._use_native_unicode = use_native_unicode

        self._engine = None
        self._factory = None

        self._setup()

    def _setup(self):
        kwargs = {}

        if self._database_url.get_driver_name() == 'postgresql':
            kwargs['use_native_unicode'] = self._use_native_unicode

        if self._pool_size is not None:
            kwargs['pool_size'] = self._pool_size

        self._engine = create_engine(self._database_url, **kwargs)

        if self._engine_events:
            for (name, listener) in self._engine_events:
                event.listen(self._engine, name, listener)

        self._factory = sessionmaker()
        self._factory.configure(bind=self._engine)

    def make_session(self):
        session = self._factory()

        if self._session_events:
            for (name, listener) in self._session_events:
                event.listen(session, name, listener)

        return session

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


def make_session_factory(database_url,
                         pool_size=None,
                         use_native_unicode=True,
                         engine_events=None,
                         session_events=None):
    return SessionFactory(database_url, pool_size, use_native_unicode,
                          engine_events, session_events)


class _declarative_base:
    def __init__(self):
        self._instance = None

    def __call__(self):
        if not self._instance:
            self._instance = sa_declarative_base()
        return self._instance


declarative_base = _declarative_base()
