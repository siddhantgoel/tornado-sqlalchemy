from ._common import BaseTestCase, User


class SessionFactoryTestCase(BaseTestCase):
    def test_make_session(self):
        session = self.factory.make_session()

        self.assertTrue(session)
        self.assertEqual(session.query(User).count(), 0)

        session.close()
