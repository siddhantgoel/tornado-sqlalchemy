from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


class MissingFactoryError(Exception):
    pass


def make_session_factory(database_url, pool_size, engine_events):
    engine = create_engine(database_url, pool_size=pool_size)

    for (name, listener) in engine_events:
        event.listen(engine, name, listener)

    factory = sessionmaker()
    factory.configure(bind=engine)

    return factory


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
