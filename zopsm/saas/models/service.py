# -*- coding: utf-8 -*-

from datetime import datetime
from zopsm.lib.credis import ZRedis
from zopsm.lib.sd_redis import redis_db_pw
import os
from sqlalchemy import event, Column, String, ForeignKey, Integer, UniqueConstraint, Boolean, DateTime
from sqlalchemy.orm import relationship
from zopsm.saas.models import Base
from zopsm.saas.utility import init_zops_models
from zopsm.saas.utility import delete_consumers_tokens

master = os.getenv('REDIS_HOST')

cache = ZRedis(host=master,
               password=redis_db_pw,
               db=os.getenv('REDIS_DB'))



class Service(Base):
    __tablename__ = 'services'

    # Are the data types of the limits BigInteger ?
    # todo : BigInteger?
    _id = Column("id", String(32), primary_key=True)
    project_id = Column(String(32), ForeignKey('projects.id'))
    service_catalog_code = Column(String(32), ForeignKey('service_catalogs.code_name'))
    account_id = Column(String(32), ForeignKey('accounts.id'))

    name = Column(String(70))
    description = Column(String(200))

    creation_time = Column("creation_time", DateTime, default=datetime.utcnow())
    last_update_time = Column("last_update_time", DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, index=True, default=False)
    is_active = Column(Boolean, index=True, default=True)

    item_used = Column(Integer, default=0)
    item_limit = Column(Integer)

    service_event = relationship('ServiceEvent', cascade="save-update, delete", backref="service")

    __table_args__ = (
        UniqueConstraint('project_id', 'service_catalog_code', 'account_id', name='account_project_service_uc'),
    )

    @property
    def id(self):
        return self._id

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        init_zops_models(self)

    def __repr__(self):
        return "<Service {} on {}>".format(self.id, self.project_id)

    def is_item_limit_available(self):
        return self.item_limit > self.item_used


@event.listens_for(Service, 'after_update')
def receive_after_update(mapper, connection, service):
    """
    if service consume all item limit then service's consumers's refresh and access token removed redis

    :param mapper:
    :param connection:
    :param service: updated service object
    :return:
    """
    if not service.is_item_limit_available():
        delete_consumers_tokens(service.project_id, service.service_catalog_code)


class ServiceCatalog(Base):
    __tablename__ = 'service_catalogs'

    _id = Column("id", String(32), primary_key=True)
    code_name = Column(String, unique=True, primary_key=True, autoincrement=False)

    creation_time = Column("creation_time", DateTime)
    last_update_time = Column("last_update_time", DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, index=True, default=False)
    is_active = Column(Boolean, index=True, default=True)

    name = Column(String(70))
    description = Column(String(200))

    @property
    def id(self):
        return self._id

    def __init__(self, *args, **kwargs):
        super(ServiceCatalog, self).__init__(*args, **kwargs)
        init_zops_models(self)

    def __repr__(self):
        return "<ServiceCatalog {}>".format(self.id)
