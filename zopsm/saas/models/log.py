from sqlalchemy import Column, String, Integer, DateTime, Text
from zopsm.saas.models import Base
from zopsm.saas.utility import init_zops_models


class Log(Base):
    __tablename__ = 'logs'

    _id = Column("id", String(32), primary_key=True)
    description = Column(Text())
    level_name = Column(String(20))
    function_name = Column(String(70))
    line_number = Column(String(5))
    path_name = Column(String(120))

    creation_time = Column("creation_time", DateTime)

    @property
    def id(self):
        return self._id

    def __init__(self, *args, **kwargs):
        super(Log, self).__init__(*args, **kwargs)
        init_zops_models(self)
