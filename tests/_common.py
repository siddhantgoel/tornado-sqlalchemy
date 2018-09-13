from unittest import TestCase

from sqlalchemy import BigInteger, Column, String

from tornado_sqlalchemy import declarative_base, make_session_factory


postgres_url = 'postgres://t_sa:t_sa@localhost/t_sa'

mysql_url = 'mysql://t_sa:t_sa@localhost/t_sa'

sqlite_url = 'sqlite:///t_sa.sqlite3'

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(64), unique=True)

    def __init__(self, username):
        self.username = username


class BaseTestCase(TestCase):
    def setUp(self):
        self.factory = make_session_factory(postgres_url)

        Base.metadata.create_all(self.factory.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.factory.engine)
