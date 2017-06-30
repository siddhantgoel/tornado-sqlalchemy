from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


class SessionMissingException(Exception):
    pass


def session_factory(database_url, pool_size, engine_events):
    engine = create_engine(database_url, pool_size=pool_size)

    for (name, listener) in engine_events:
        event.listen(engine, name, listener)

    factory = sessionmaker()
    factory.configure(bind=engine)

    return factory


class SessionMixin(object):
    def prepare(self):
        self.session = self.application.session_factory()

    def on_finish(self):
        try:
            self.session.commit()
        finally:
            self.session.close()

    def send_error(self, status_code=500, **kwargs):
        result = super(SessionMixin, self).send_error(status_code, **kwargs)

        try:
            self.session.rollback()
        finally:
            self.session.close()

        return result
