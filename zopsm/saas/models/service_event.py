from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from zopsm.saas.models import Base
from zopsm.saas.utility import init_zops_models


class ServiceEvent(Base):
    __tablename__ = 'service_events'

    _id = Column("id", String(32), primary_key=True)
    service_id = Column(String(32), ForeignKey('services.id'))
    name = Column(String(40))
    amount = Column(Integer, default=0)
    creation_time = Column("creation_time", DateTime)

    @property
    def id(self):
        return self._id

    def __init__(self, *args, **kwargs):
        super(ServiceEvent, self).__init__(*args, **kwargs)
        init_zops_models(self)
