import os
import time
from unittest import mock

from tornado.testing import AsyncTestCase, gen_test
from tornado_sqlalchemy import as_future, set_max_workers

from ._common import db, User, mysql_url

set_max_workers(10)
os.environ['ASYNC_TEST_TIMEOUT'] = '100'


class ConcurrencyTestCase(AsyncTestCase):
    session_count = 3
    sleep_duration = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        db.configure(uri=mysql_url, engine_options={'echo': True})
        self.application = mock.Mock()
        self.application.settings = {'db': db}

    def setUp(self) -> None:
        super().setUp()
        db.create_all()

    def tearDown(self) -> None:
        db.drop_all()
        super().tearDown()

    def test_echo(self):
        session = db.sessionmaker()
        count = session.query(User).count()
        session.close()

        assert count == 0

    @gen_test
    def test_concurrent_requests_using_yield(self):

        sessions = [db.sessionmaker() for _ in range(self.session_count)]

        t = time.time()
        yield [
            as_future(
                lambda: session.execute(
                    'SELECT sleep(:duration)',
                    {'duration': self.sleep_duration},
                )
            )
            for session in sessions
        ]

        print('yield:', time.time() - t)

        for session in sessions:
            session.close()

    @gen_test
    async def test_concurrent_requests_using_async(self):

        sessions = [db.sessionmaker() for _ in range(self.session_count)]

        t = time.time()

        for session in sessions:
            await as_future(
                lambda: session.execute(
                    'SELECT sleep(:duration)',
                    {'duration': self.sleep_duration},
                )
            )

        print('await:', time.time() - t)
        for session in sessions:
            session.close()
