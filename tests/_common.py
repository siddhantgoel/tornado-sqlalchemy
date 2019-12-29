from unittest import TestCase, mock

from sqlalchemy import BigInteger, Column, String

from tornado_sqlalchemy import SQLAlchemy


postgres_url = 'postgresql://t_sa:t_sa@localhost/t_sa'

mysql_url = 'mysql://t_sa:t_sa@localhost/t_sa'
mysql_url_1 = 'mysql://t_sa:t_sa@localhost/t_sa_1'
mysql_url_2 = 'mysql://t_sa:t_sa@localhost/t_sa_2'

sqlite_url = 'sqlite:///t_sa.sqlite3'


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(64), unique=True)

    def __init__(self, username):
        self.username = username


class BaseTestCase(TestCase):
    def setUp(self):
        self.db_uri = mysql_url

        db.configure(uri=mysql_url)

        self.application = mock.Mock()
        self.application.settings = {'db': db}

        db.create_all()

    def tearDown(self):
        db.drop_all()
