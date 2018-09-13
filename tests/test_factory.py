from unittest import TestCase

from tornado_sqlalchemy import make_session_factory

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
