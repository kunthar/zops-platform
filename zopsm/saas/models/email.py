from sqlalchemy import Column, String, DateTime, Enum
from zopsm.saas.models import Base
from zopsm.saas.utility import init_zops_models


class Email(Base):
    __tablename__ = 'emails'

    _id = Column("id", String(32), primary_key=True)
    account_id = Column(String(32))

    category = Column(Enum("info", "approve", "statistic", "reset_password", name="mail_category"))
    provider = Column(String(30))
    receiver = Column(String(70))
    provider_mail_id = Column("mail_id", String(70), unique=True)

    subject = Column("subject", String(120))
    text = Column("text", String(400))

    creation_time = Column("creation_time", DateTime)

    @property
    def id(self):
        return self._id

    def __init__(self, *args, **kwargs):
        super(Email, self).__init__(*args, **kwargs)

        init_zops_models(self)

    def __repr__(self):
        return "<Mail on{}".format(self.account_id)
