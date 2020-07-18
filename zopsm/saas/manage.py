# -*- coding: utf-8 -*-

import sys
import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from subprocess import call
from zopsm.saas.config import *
import configparser

param = sys.argv[1]


def change_sqlalchemy_uri(new_uri):
    """
    Change alembic.ini file. Set sqlalchemy.url with config file's url.
    Args:
        new_uri:
    """
    alembic_parser = configparser.ConfigParser()
    alembic_parser.read('alembic.ini')
    alembic_parser['alembic']['sqlalchemy.url'] = new_uri
    with open('alembic.ini', 'w') as configfile:
        alembic_parser.write(configfile)


def load_enviroment_to_alembic():
    """
    Load Base metadata to alembic/env.py file
    """
    fp = open('alembic/env.py', 'r+')
    lines = fp.readlines()
    lines[17] = 'from zopsm.saas.models import Base\ntarget_metadata = Base.metadata'
    fp.seek(0)
    fp.writelines(lines)
    fp.close()


def init():
    try:
        call(['rm', '-r', 'alembic'])
        os.remove('alembic.ini')
    except Exception as e:
        pass
    finally:
        call(['alembic', 'init', 'alembic'])
        change_sqlalchemy_uri(SQLALCHEMY_DATABASE_URI)
        load_enviroment_to_alembic()


def migrate():
    # update_models()
    call(['alembic', 'revision', '--autogenerate'])


def upgrade():
    call(['alembic', 'upgrade', 'head'])


def reset():
    init()
    migrate()
    upgrade()

if param == 'init':
    init()

elif param == 'migrate':
    migrate()

elif param == 'upgrade':
    upgrade()

elif param == 'current':
    call(['alembic', 'current'])

elif param == 'reset':
    reset()

elif param == 'update':
    migrate()
    upgrade()
