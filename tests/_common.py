from unittest import TestCase, mock

from sqlalchemy import BigInteger, Column, String

from tornado_sqlalchemy import SQLAlchemy


postgres_url = 'postgresql://t_sa:t_sa@127.0.0.1:5432/t_sa'

mysql_url = 'mysql+mysqldb://t_sa:t_sa@127.0.0.1:3306/t_sa'
mysql_url_1 = 'mysql+mysqldb://t_sa:t_sa@127.0.0.1:3306/t_sa_1'
mysql_url_2 = 'mysql+mysqldb://t_sa:t_sa@127.0.0.1:3306/t_sa_2'

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
        self.db_url = mysql_url

        db.configure(url=mysql_url)

        self.application = mock.Mock()
        self.application.settings = {'db': db}

        db.create_all()

    def tearDown(self):
        db.drop_all()
