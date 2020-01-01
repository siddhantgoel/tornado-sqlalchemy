import os
from unittest import mock

from tornado.testing import AsyncTestCase, gen_test
from tornado_sqlalchemy import as_future, set_max_workers

from ._common import db, User, mysql_url

set_max_workers(10)
os.environ['ASYNC_TEST_TIMEOUT'] = '100'


class ConcurrencyTestCase(AsyncTestCase):
    session_count = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        db.configure(uri=mysql_url)

        self.application = mock.Mock()
        self.application.settings = {'db': db}

    def setUp(self) -> None:
        super().setUp()

        db.create_all()

    def tearDown(self) -> None:
        db.drop_all()

        super().tearDown()

    @gen_test
    def test_concurrent_requests_using_yield(self):
        sessions = [db.sessionmaker() for _ in range(self.session_count)]

        for index, session in enumerate(sessions):
            session.add(User('User #{}'.format(index)))
        session.commit()

        yield [as_future(session.query(User).count) for session in sessions]

        for session in sessions:
            session.close()

    @gen_test
    async def test_concurrent_requests_using_async(self):
        sessions = [db.sessionmaker() for _ in range(self.session_count)]

        for index, session in enumerate(sessions):
            session.add(User('User #{}'.format(index)))
        session.commit()

        for session in sessions:
            await as_future(session.query(User).count)

        for session in sessions:
            session.close()
