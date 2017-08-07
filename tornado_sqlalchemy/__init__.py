from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base as _declarative_base
from sqlalchemy.orm import sessionmaker


__all__ = ['SessionMixin', 'set_max_workers', 'as_future',
           'make_session_factory', 'declarative_base']


class MissingFactoryError(Exception):
    pass


class _AsyncExecution(object):
    """Tiny wrapper around ThreadPoolExecutor. This class is not meant to be
    instantiated externally, but internally we just use it as a wrapper around
    ThreadPoolExecutor so we can control the pool size and make the
    `as_future` function public.
    """

    _default_max_workers = 5

    def __init__(self, max_workers=None):
        self._max_workers = max_workers or self._default_max_workers
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    def set_max_workers(self, count):
        if self._pool:
            self._pool.shutdown(wait=True)

        self._max_workers = count
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    def as_future(self, query):
        """Wrap a `sqlalchemy.orm.query.Query` object into a
        `concurrent.futures.Future` so that it can be yielded.

        :param query: `sqlalchemy.orm.query.Query` object
        :returns: `concurrent.futures.Future` object wrapping the given query
        so that tornado can yield on it.
        """
        return self._pool.submit(query)


class SessionFactory(object):
    """SessionFactory is a wrapper around the functions that SQLAlchemy
    provides. The intention here is to let the user work at the session level
    instead of engines and connections.

    :param database_url: Database URL
    :param pool_size: Connection pool size
    :param use_native_unicode: Enable/Disable native unicode support
    :param engine_events: List of (name, listener_function) tuples to subscribe
    to engine events
    :param session_events: List of (name, listener_function) tuples to
    subscribe to session events
    """

    def __init__(self, database_url, pool_size=None, use_native_unicode=True,
                 engine_events=None, session_events=None):
        self._database_url = database_url
        self._pool_size = pool_size
        self._engine_events = engine_events
        self._session_events = session_events
        self._use_native_unicode = use_native_unicode

        self._engine = None
        self._factory = None

        self._setup()

    def _setup(self):
        kwargs = {
            'use_native_unicode': self._use_native_unicode
        }

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


class SessionMixin(object):
    @contextmanager
    def make_session(self):
        factory = self.application.settings.get('session_factory')

        if not factory:
            raise MissingFactoryError()

        try:
            session = factory.make_session()

            yield session
        except:
            session.rollback()
            raise
        else:
            session.commit()
        finally:
            session.close()


_async_exec = _AsyncExecution()

set_max_workers = _async_exec.set_max_workers

as_future = _async_exec.as_future


def make_session_factory(database_url,
                         pool_size=None,
                         use_native_unicode=True,
                         engine_events=None,
                         session_events=None):
    return SessionFactory(database_url, pool_size, use_native_unicode,
                          engine_events, session_events)


def declarative_base():
    if not declarative_base._instance:
        declarative_base._instance = _declarative_base()
    return declarative_base._instance


declarative_base._instance = None
