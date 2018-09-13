from unittest import TestCase

from tornado_sqlalchemy import declarative_base


class DeclarativeBaseTestCase(TestCase):
    def test_multiple_calls_return_the_same_instance(self):
        first = declarative_base()
        second = declarative_base()

        self.assertTrue(first is second)
        self.assertEqual(id(first), id(second))
