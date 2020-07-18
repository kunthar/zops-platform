# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import String, Column, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from zopsm.saas.models import Base
from zopsm.saas.utility import init_zops_models


class Consumer(Base):
    __tablename__ = 'consumers'

    _id = Column("id", String(32), primary_key=True)
    account_id = Column(String(32), ForeignKey('accounts.id'))

    creation_time = Column("creation_time", DateTime)
    last_update_time = Column("last_update_time", DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, index=True, default=False)
    is_active = Column(Boolean, index=True, default=True)

    project_consumers = relationship('ProjectConsumer', cascade="save-update, delete", backref="consumer")

    @property
    def id(self):
        return self._id

    def __init__(self, *args, **kwargs):
        super(Consumer, self).__init__(*args, **kwargs)
        init_zops_models(self)

    def __repr__(self):
        return "<Consumer {} on {}>".format(self._id, self.account_id)


class ProjectConsumer(Base):
    __tablename__ = 'project_consumers'

    _id = Column("id", String(32), primary_key=True)
    project_id = Column(String(32), ForeignKey('projects.id'))
    consumer_id = Column(String(32), ForeignKey('consumers.id'))
    creation_time = Column("creation_time", DateTime)

    @property
    def id(self):
        return self._id

    def __init__(self, *args, **kwargs):
        super(ProjectConsumer, self).__init__(*args, **kwargs)
        init_zops_models(self)

    def __repr__(self):
        return "<ProjectConsumer {} on {}>".format(self.consumer_id, self.project_id)
