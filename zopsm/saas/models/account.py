# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from zopsm.saas.models import Base
from zopsm.saas.utility import init_zops_models


class Account(Base):
    __tablename__ = 'accounts'

    _id = Column("id", String(32), primary_key=True)
    tenant_id = Column(String(32), ForeignKey('tenants.id'))
    email = Column(String(70), unique=True)

    project_limit = Column(Integer)
    project_used = Column(Integer, default=0)

    approve_code = Column(String(64))
    organization_name = Column("organization_name", String(100))
    address = Column("address", String(200))
    phone = Column("phone", String(11))

    creation_time = Column("creation_time", DateTime)
    last_update_time = Column("last_update_time", DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)

    managers = relationship('User', cascade="save-update, delete", backref="account")
    projects = relationship('Project', cascade="save-update, delete", backref="account")
    consumers = relationship('Consumer', cascade="save-update, delete", backref="account")

    @property
    def id(self):
        return self._id

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        init_zops_models(self)

    def __repr__(self):
        return "<Account {} on {}>".format(self.email, self.tenant_id)
