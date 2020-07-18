# -*- coding: utf-8 -*-

from sqlalchemy import desc, asc
from falcon.errors import HTTPInternalServerError, HTTPNotFound, HTTPConflict
from zopsm.saas.models import User, Project, Service, Consumer, Account, ProjectConsumer, Email, Log
from zopsm.saas.log_handler import saas_logger
from zopsm.saas.utility import data_hashing
from zopsm.lib.credis import ZRedis
from zopsm.lib.sd_redis import redis_db_pw
import os

master = os.getenv('REDIS_HOST')

cache = ZRedis(host=master,
               password=redis_db_pw,
               db=os.getenv('REDIS_DB'))

CRITICAL_ERROR_MESSAGE = "Critical error occurred. We handle this error as soon as possible"


class SimpleDBHandler(object):
    def append_default_params(self, **kwargs):
        """
        Append default params with default context.

        Args:
            **kwargs:

        Returns:
            dict:
        """

        kwargs["is_active"] = kwargs.get("is_active", True)
        kwargs["is_deleted"] = kwargs.get("is_deleted", False)

        return kwargs

    def get(self, model, **kwargs):
        """
        Get data from database.
        Args:
            model: Which model class used to get data
            **kwargs: Extra conditions for filtering data.
        Returns:
            model: Data. If data not found return None
        """
        # params = self.append_default_params(**kwargs)
        try:
            q = self.session.query(model).filter_by(**kwargs)
            return q.scalar()

        except Exception as e:
            saas_logger.error(e)
            raise HTTPInternalServerError(description=CRITICAL_ERROR_MESSAGE)

    def filter(self, model, order_field=None, descending=True, **kwargs):
        """

        :param model:
        :param order_field:
        :param descending:
        :param kwargs:
        :return:
        """
        # params = self.append_default_params(**kwargs)
        try:
            q = self.session.query(model).filter_by(**kwargs)
            if order_field:
                order_field = getattr(model, order_field)
                if descending:
                    q = q.order_by(desc(order_field))
                else:
                    q = q.order_by(asc(order_field))
            return q.all()
        except Exception as e:
            saas_logger.error(e)
            raise HTTPInternalServerError(description=CRITICAL_ERROR_MESSAGE)

    def paginated_filter(self, model, order_field, page_size, page, descending=True, **kwargs):
        """
        Filter with page size, page, model, and order_field

        If you want to take first 20 log row sorting with descending order and filtered with kwargs value
        example: paginated_filter(Log,Log.creation_time, 20, 0, **kwargs)

        paginated_filter
        :param model: model
        :param order_field: order field format model.field
        :param page_size:
        :param page:
        :param descending: default true. if descending set false then sorted with ascending order
        :param kwargs: filter parameters
        """
        try:
            order = desc(order_field) if descending else asc(order_field)
            q = self.session.query(model).filter_by(**kwargs)
            return q.order_by(order).limit(page_size).offset(page * page_size).all()

        except Exception as e:
            saas_logger.error(e)
            raise HTTPInternalServerError(description=CRITICAL_ERROR_MESSAGE)

    def count(self, model, **kwargs):
        """

        :param model: model
        :param kwargs: filter parameters
        :return: number of row
        """
        try:
            return self.session.query(model).filter_by(**kwargs).count()
        except Exception as e:
            saas_logger.error(e)
            raise HTTPInternalServerError(description=CRITICAL_ERROR_MESSAGE)

    def exists(self, model, **kwargs):
        """
        Check the `model` with `**kwargs` for existence.
        Args:
            model:
            **kwargs:

        Returns:
            Bool: If exists, return True.
        """
        return True if self.get(model=model, **kwargs) else False


class ResourceDB(SimpleDBHandler):
    def __init__(self, session):
        self.session = session

    def get_object(self, model, **kwargs):
        obj = self.get(model=model, **kwargs)
        if obj:
            return obj

        raise HTTPNotFound(description="Resource object does not exist.")

    def create_user(self, validated, jwt_token, role):
        """
        Create a account user according in jwt_token's `account_id`.
            if email address already exist raise httpconflict error.
            if we don't have conflict, user created given parameters(email, password, role, account_id, first_name, last_name)
            and changes committed.
        Args:
            validated: (Dict)
            jwt_token: (Dict)
            role: (ERoles)

        Returns:
            dict: Repr of the resource
        """
        hashed_password = data_hashing(validated['password'])
        if self.exists(model=User, email=validated['email']):
            raise HTTPConflict(description="This email address used by another user.")

        user = User(email=validated['email'], password=hashed_password, role=role,
                    account_id=jwt_token['account_id'], first_name=validated['first_name'],
                    last_name=validated['last_name'])

        self.session.add(user)

        return user

    def _get_user(self, user_id, account_id):
        """
        Just get user by `user_id`, `account_id`
        Args:
            user_id:
            account_id:
        Returns:
            User:
        """
        return self.get_object(model=User, _id=user_id, account_id=account_id)

    def get_user(self, user_id, account_id):
        """
        Get user according to `user_id` and `account_id`. For reusability
        Args:
            user_id:
            account_id: This parameter allows us that just client can see own users.
        Returns:
            dict: Validated, repr of resource
        """
        return self._get_user(user_id, account_id)

    def update_user(self, user_id, validated, account_id):
        """
        Update user information
        If new email address already exist raise httpconflict error
        There is no such conflict then user updated given parameters(email, password, first_name, last_name)
        Args:
            user_id:
            validated:
            account_id: Client can see and update own users.
        Returns:
            User: Updated user.
        """

        user = self._get_user(user_id, account_id)

        if user.email != validated['email']:
            if self.get(model=User, email=validated['email']):
                raise HTTPConflict(description="This email address used by another user")

        user.email = validated['email']
        user.password = validated['password']
        user.first_name = validated['first_name']
        user.last_name = validated['last_name']

        return user

    def login(self, email, password):
        """

        :param email: user email
        :param password: user password
        :return: User.
        """
        user = self.get_object(model=User, email=email, password=password)
        return user

    def delete_user(self, user_id, account_id):
        """
        Delete user with account id and user id. Deleted users token key deleted from redis
        :param user_id:
        :param account_id:
        :return:
        """
        user = self._get_user(user_id, account_id)

        self.session.delete(user)

    def delete_admin(self, user_id, account_id, role):
        """
        Delete admin user. If account has only one admin user then deletion rejected. Because of every account
        must have at least one admin user

        :param user_id: want to delete user's id
        :param account_id: user's account id
        :param role:User role : admin
        """
        admins = self.filter(model=User, account_id=account_id, role=role)
        if len(admins) > 1:
            self.delete_user(user_id, account_id)
        else:
            raise HTTPNotFound(description="Deletion not completed.Your account only have 1 admin user.")
            # todo:http status ?

    def delete_account(self, account_id):
        """
        Delete account with given account_id if it is valid account_id. All account users's tokens deleted from redis
        :param account_id:
        :return:
        """
        account = self.get_object(model=Account, _id=account_id)

        self.session.delete(account)

    def update_account(self, account_id, validated):
        """
        Update account with given values

        :return: Account object
        """
        account = self.get_object(model=Account, _id=account_id)
        account.organization_name = validated['organization_name']
        account.address = validated['address']
        account.phone = validated['phone']
        account.email = validated['email']
        return account

    def get_account(self, account_id):
        return self.get_object(model=Account, _id=account_id)

    def get_account_with_email(self, email):
        return self.get_object(model=Account, email=email)

    def get_project(self, project_id, account_id):
        return self.get_object(model=Project, _id=project_id, account_id=account_id)

    def list_user_by_role(self, account_id, role):
        """
        List all user
        Args:
            account_id: Which account
            role: Which role (ERoles)
        Returns:
            List: List of User
        """
        return self.filter(model=User, account_id=account_id, role=role)

    def get_project_by_id(self, project_id, account_id):
        """
        Get project by `project_id` and `account_id`
        Args:
            project_id:
            account_id:
        Returns:
            Project:
        """
        return self.get_object(model=Project, _id=project_id, account_id=account_id)

    def get_service_of_project(self, service_catalog_code, project_id, account_id):
        """
        Get service informations according to `service_code` `project_id` `account_id`
        Args:
            service_catalog_code:
            project_id:
            account_id:

        Returns:
            Service:
        """
        return self.get_object(model=Service, service_catalog_code=service_catalog_code, project_id=project_id,
                               account_id=account_id)

    def get_service(self, project_id, service_catalog_code):
        return self.get_object(model=Service, project_id=project_id, service_catalog_code=service_catalog_code)

    def get_consumer_by_id(self, consumer_id, account_id):
        """
        Get concumer infoermation according to "service_code", "prorject_id", "account_id"
        Args:
            consumer_id:
            account_id:
        Returns:
            Consumer:
        """
        return self.get_object(model=Consumer, _id=consumer_id, account_id=account_id)

    def get_attached_consumer(self, consumer_id, project_id):
        """
        Check, the consumer already attached to project.
        Args:
            consumer_id:
            project_id:

        Returns:
            ProjectConsumer: If attached return ProjectConsumer object, if not return None
        """
        return self.get(model=ProjectConsumer, consumer_id=consumer_id, project_id=project_id)

    def email_filter(self, **kwargs):
        return self.filter(model=Email, order_field="creation_time", **kwargs)

