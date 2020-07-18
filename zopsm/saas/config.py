import os
from zopsm.lib import sd_postgres
from zopsm.lib.log_handler import zlogger

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY')

DB_USER=sd_postgres.postgres_user
DB_PASSWORD=sd_postgres.postgres_pw

DB_NAME = os.environ.get('DB_NAME')
DB_HOST = sd_postgres.watch_postgres(single=True)
DB_PORT = os.environ.get('DB_PORT')

REDIS_HOST = os.environ.get('REDIS_HOST', "127.0.0.1")
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(DB_USER,
                                                                        DB_PASSWORD,
                                                                        DB_HOST,
                                                                        DB_PORT,
                                                                        DB_NAME)

