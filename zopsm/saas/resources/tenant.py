# -*- coding: utf-8 -*-

import datetime
from falcon.errors import HTTPConflict, HTTPMethodNotAllowed
from graceful.fields import StringField
from graceful.resources.generic import ListCreateAPI, RetrieveUpdateDeleteAPI
from zopsm.saas.auth import require_roles
from zopsm.saas.models import Tenant, User, ERoles
from zopsm.saas.validators import phone_validator, email_validator
from zopsm.saas.resources.saas_base import SaasBase
from zopsm.lib.rest.serializers import ZopsBaseSerializer
from zopsm.saas.utility import encode_jwt_token


class TenantSerializer(ZopsBaseSerializer):
    email = StringField("email for user", validators=[email_validator])
    password = StringField("password for user")
    organizationName = StringField("organization name", source='organization_name')
    address = StringField("physical address")
    phone = StringField("phone number, length must be 11 character.", validators=[phone_validator])
    tenantEmail = StringField("email for tenant", source='tenant_email')
    tenantId = StringField("ID for tenant", read_only=True, source='tenant_id')
    managerToken = StringField("auth token of tenant manager", read_only=True, source='manager_token')


class TenantSingleSerializer(ZopsBaseSerializer):
    organizationName = StringField("organization name", source='organization_name')
    address = StringField("physical address")
    phone = StringField("phone number, length must be 11 character.", validators=[phone_validator])
    email = StringField("email for tenant")


class TenantResource(SaasBase, ListCreateAPI):
    serializer = TenantSerializer()

    def __repr__(self):
        return "Tenant Create"

    def resource_name(self):
        return "TenantResource"

    def check_tenant_exists(self, **kwargs):
        if self.db.get_tenant(**kwargs):
            raise HTTPConflict(title='Tenant exists, 409',
                               description='Tenant has already exist, nothing to do!')

    @require_roles(roles=[ERoles.manager])
    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')

        self.check_tenant_exists(email=validated['tenant_email'])

        tenant = Tenant(email=validated['tenant_email'],
                        address=validated['address'],
                        organization_name=validated['organization_name'],
                        phone=validated['phone'])
        user = User(email=validated['email'],
                    password=validated['password'],
                    role=ERoles.manager)

        tenant.managers.append(user)

        # Record JWT token expire time.
        iat = datetime.datetime.utcnow()
        exp = iat + datetime.timedelta(weeks=1)
        user.auth_token = encode_jwt_token(user.id, exp=exp, iat=iat, role=ERoles.manager.value, tenant_id=tenant.id)

        self.db.session.add(tenant)

        validated['manager_token'] = user.auth_token
        validated['tenant_id'] = tenant.id
        return validated

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class TenantResourceSingle(SaasBase, RetrieveUpdateDeleteAPI):
    serializer = TenantSingleSerializer()

    def __repr__(self):
        return "Tenant Retrieve & Update & Delete"

    def resource_name(self):
        return "TenantResourceSingle"

    @require_roles(roles=[ERoles.manager])
    def retrieve(self, params, meta, **kwargs):
        tenant_id = kwargs.get('tenant_id')
        tenant = self.db.get_tenant(_id=tenant_id)
        print(tenant)
        return tenant

    @require_roles(roles=[ERoles.manager])
    def update(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        tenant = self.db.get_tenant(_id=kwargs.get('tenant_id'))
        self.db.update_tenant(tenant, validated)
        return tenant

    @require_roles(roles=[ERoles.manager])
    def delete(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())
