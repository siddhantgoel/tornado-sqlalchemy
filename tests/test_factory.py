from unittest import TestCase

from tornado.testing import AsyncTestCase, gen_test
from tornado_sqlalchemy import as_future, make_session_factory

from ._common import Base, User, mysql_url, postgres_url, sqlite_url


class FactoryTestCase(TestCase):
    def _test_with_factory(self, factory):
        self.assertTrue(factory)

        Base.metadata.create_all(factory.engine)

        session = factory.make_session()

        self.assertTrue(session)
        self.assertEqual(session.query(User).count(), 0)

        session.close()

        Base.metadata.drop_all(factory.engine)

    def test_make_mysql_factoy(self):
        self._test_with_factory(make_session_factory(mysql_url))

    def test_make_postgres_factory(self):
        self._test_with_factory(make_session_factory(postgres_url))

    def test_make_sqlite_factory(self):
        self._test_with_factory(make_session_factory(sqlite_url))


class ConcurrencyTestCase(AsyncTestCase):
    session_count = 5
    sleep_duration = 5

    @gen_test
    def test_concurrent_requests_using_yield(self):
        factory = make_session_factory(postgres_url, pool_size=1)

        sessions = [factory.make_session() for _ in range(self.session_count)]

        yield [
            as_future(
                lambda: session.execute(
                    'SELECT pg_sleep(:duration)',
                    {'duration': self.sleep_duration},
                )
            )
            for session in sessions
        ]

        for session in sessions:
            session.close()

    @gen_test
    async def test_concurrent_requests_using_async(self):
        factory = make_session_factory(postgres_url, pool_size=1)

        sessions = [factory.make_session() for _ in range(self.session_count)]

        for session in sessions:
            await as_future(
                lambda: session.execute(
                    'SELECT pg_sleep(:duration)',
                    {'duration': self.sleep_duration},
                )
            )

        for session in sessions:
            session.close()
