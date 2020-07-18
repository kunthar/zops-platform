from graceful.resources.generic import ListAPI
from graceful.parameters import StringParam
from graceful.fields import StringField
from zopsm.lib.rest.serializers import ZopsBaseSerializer
from zopsm.saas.auth import require_roles
from zopsm.saas.models import ERoles
from zopsm.saas.resources.saas_base import SaasBase


class EmailSerializer(ZopsBaseSerializer):
    accountId = StringField("Account id", read_only=True, source="account_id")
    providerMailId = StringField("Provider mail id", read_only=True, source="provider_mail_id")
    receiver = StringField("Email address.", read_only=True)
    subject = StringField("Email subject", read_only=True)
    text = StringField("Email text", read_only=True)
    provider = StringField("Email provider", read_only=True)
    category = StringField("Email category", read_only=True)


class EmailTrackingResource(SaasBase, ListAPI):
    allow_in_public_doc = False
    serializer = EmailSerializer()

    receiver = StringParam("Filter mail by email address")
    account_id = StringParam("Filter mail by account_id")
    provider_mail_id = StringParam("Filter mail by mailgun mail id")

    def __repr__(self):
        return "Get Email Information"

    def resource_name(self):
        return "EmailTrackingResource"

    @require_roles(roles=[ERoles.manager])
    def list(self, params, meta, **kwargs):
        params.pop("indent")
        return self.db.email_filter(**params)

