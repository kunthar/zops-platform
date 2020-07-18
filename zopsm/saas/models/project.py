# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, LargeBinary, Integer
from sqlalchemy.orm import relationship
from zopsm.saas.models import Base
from zopsm.saas.utility import init_zops_models


class Project(Base):
    __tablename__ = 'projects'

    _id = Column("id", String(32), primary_key=True)
    account_id = Column(String(32), ForeignKey('accounts.id'))

    name = Column(String(70))
    description = Column(String(200))

    user_limit = Column(Integer, default=10)
    user_used = Column(Integer, default=0)

    creation_time = Column("creation_time", DateTime)
    last_update_time = Column("last_update_time", DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, index=True, default=False)
    is_active = Column(Boolean, index=True, default=True)

    fcm_api_key = Column("google_server_api_key", String(255), default=None)
    fcm_project_number = Column("google_project_number", String(255), default=None)
    apns_cert = Column("apns_ios_push_certificate", LargeBinary, default=None)

    services = relationship('Service', cascade="save-update, delete", backref="project")
    project_consumers = relationship('ProjectConsumer', cascade="save-update, delete", backref="project")

    @property
    def id(self):
        return self._id

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        init_zops_models(self)

    def __repr__(self):
        return "<Project {} on {}>".format(self.id, self.account_id)

    def is_user_limit_available(self):
        return self.user_limit > self.user_used


