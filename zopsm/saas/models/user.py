# -*- coding: utf-8 -*-

import enum
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Enum, Boolean, DateTime
from zopsm.saas.models import Base
from zopsm.saas.utility import init_zops_models


class ERoles(enum.Enum):
    root = 0
    manager = 1
    admin = 2
    developer = 3
    billing = 4
    anonym = 5


class User(Base):
    __tablename__ = 'users'

    _id = Column("id", String(32), primary_key=True)
    email = Column("email", String(70), unique=True)
    tenant_id = Column(String(32), ForeignKey('tenants.id'))
    account_id = Column(String(32), ForeignKey('accounts.id'))

    first_name = Column("first_name", String(32))
    last_name = Column("last_name", String(32))

    password = Column("password", String(128))
    role = Column(Enum(ERoles))

    creation_time = Column("creation_time", DateTime)
    last_update_time = Column("last_update_time", DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, index=True, default=False)
    is_active = Column(Boolean, index=True, default=True)

    @property
    def id(self):
        return self._id

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        init_zops_models(self)

    def __repr__(self):
        return "<User {}".format(self.email)
