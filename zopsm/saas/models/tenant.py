# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from zopsm.saas.models import Base
from zopsm.saas.utility import init_zops_models


class Tenant(Base):
    __tablename__ = 'tenants'

    _id = Column("id", String(32), primary_key=True)

    email = Column(String(70))
    organization_name = Column("organization_name", String(100))
    address = Column("address", String(200))
    phone = Column("phone", String(11))

    creation_time = Column("creation_time", DateTime)
    last_update_time = Column("last_update_time", DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, index=True, default=False)
    is_active = Column(Boolean, index=True, default=True)

    managers = relationship('User')
    accounts = relationship('Account')

    @property
    def id(self):
        return self._id

    def __init__(self, *args, **kwargs):
        super(Tenant, self).__init__(*args, **kwargs)
        init_zops_models(self)

    def __repr__(self):
        return "<Tenant {}>".format(self.email)
