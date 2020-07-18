from falcon.errors import HTTPMethodNotAllowed
from falcon.errors import HTTPConflict, HTTPNotFound
from graceful.fields import StringField
from graceful.parameters import BoolParam
from graceful.resources.generic import ListCreateAPI, RetrieveUpdateAPI
from zopsm.saas.auth import require_roles
from zopsm.saas.models import User, ERoles, Account, Email
from zopsm.saas.validators import email_validator
from zopsm.saas.resources.saas_base import SaasBase
from zopsm.saas.utility import send_account_approve_mail
from zopsm.lib.settings import ACCOUNT_LIMIT
from zopsm.lib.rest.serializers import ZopsBaseSerializer
from zopsm.saas.utility import generate_token
from zopsm.saas.utility import data_hashing
from zopsm.saas.log_handler import saas_logger
from zopsm.saas.utility import encode_jwt_token, create_auth_token_payload, add_user_token


class RegisterSerializer(ZopsBaseSerializer):
    organizationName = StringField("Organization name.Max length 100 Character", source='organization_name')
    email = StringField("Email for account.Max length 70 Character")
    registrationId = StringField("Registered account id.", read_only=True, source='id')


class RegisterSingleSerializer(ZopsBaseSerializer):
    id = StringField("ID", read_only=True)
    email = StringField("Email for user.Max length 70 Character", validators=[email_validator])
    password = StringField("Password for user.Max length 128 Character", write_only=True)
    approveCode = StringField("Approve code to activate the account.", write_only=True, source='approve_code')
    firstName = StringField("Name of user.Max length 32 Character", source='first_name')
    lastName = StringField("Last Name of user.Max length 32 Character", source='last_name')
    token = StringField("User token", read_only=True)


class ApproveCodeSerializer(ZopsBaseSerializer):
    email = StringField("Email for account.Max length 70 Character", write_only=True)


class RegisterResource(SaasBase, ListCreateAPI):
    """
    Allows to Post Register New Account

    ####### Code Example:

    ### POST:
    Create a new account
    ### Request:

    ```bash
        #bash
        curl \\
             --request POST                             \\
             --header "Content-Type: application/json"  \\
             --body "{                                                          \\
                  \"organizationName\": \"Example Organization\",               \\
                  \"email\": \"zops_test_eneoooeeN@example.com\"                \\
             }"                                                                 \\
             https://api_baseurl/api/v1/register
    ```

    ```python
        #python
        import requests
        import json

        header = {'Content-Type': 'application/json'}

        body = {
                "organizationName": "Example Organization",
                "email": "zops_test_eneoooeeN@example.com"
        }

        req = requests.post("https://api_baseurl/api/v1/register",
                                        header=header, data=json.dumps(body))
    ```

    #### Response:
    201 Created.
    ```json
        {
        "meta":{
                "params": {
                        "indent": 0
                        }
               },
        "content": {
                     "organizationName": "Example Organization",
                     "email": "zops_test_eneoooeeN@example.com",
                     "registrationId": "f200baccded4413a81f9a381063c435c",
                     }
        }
    ```
    #### Possible Errors
    - __Conflict__: Email address already used
    - __Failed Dependency__ :An Error occur on 3rd part service. Please retry after a few minutes.

    """

    serializer = RegisterSerializer()

    testing = BoolParam("Testing mode parameter.", default="False")

    def __repr__(self):
        return "Account Create"

    def resource_name(self):
        return "RegisterResource"

    @require_roles(roles=[ERoles.anonym])
    def create(self, params, meta, **kwargs):
        """
        default account type is "trial". you can see account types in zopsm.lib.setting file
        """
        validated = kwargs.get('validated')
        account = self.db.exists(Account, email=validated['email'])
        if not account:
            approve_code = generate_token()
            testing = params.get('testing')
            saas_logger.debug(testing)

            project_limit = ACCOUNT_LIMIT['project_limit']
            account = Account(approve_code=approve_code, organization_name=validated['organization_name'],
                              email=validated['email'], project_limit=project_limit)
            self.db.session.add(account)
            self.db.session.flush()

            mail_response = send_account_approve_mail(approve_code, validated['email'], account.id, testing)
            email = Email(provider_mail_id=mail_response['id'], account_id=account.id, text=mail_response['text'],
                          subject=mail_response['subject'], receiver=validated['email'], provider="MAILGUN",
                          category="approve")
            self.db.session.add(email)
        else:
            raise HTTPConflict(description="These email address already used")

        return account

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class RegisterSingleResource(SaasBase, RetrieveUpdateAPI):

    """
    Allows to update with Approve Code and Password

    ####### Code Example:

    #### PUT
    Update account with approve code and password. Create User with admin role
    ### Request:

    ```bash
        #bash
        curl \\
             --request PUT                             \\
             --header "Content-Type: application/json" \\
             --body "{                                                                                      \\
                   \"approveCode\": \"595819dca81e3ae6f81f4a39bd0470103044f936f6dd971803a23\",              \\
                   \"email\": \"zops_test_eneoooeeN@example.com\",                                          \\
                   \"password\": \"123\",                                                                   \\
                   \"firstName\": \"emre\",                                                                 \\
                   \"lastName\": \"dönmesz\"                                                                \\
             }"                                                                                             \\
             https://api_baseurl/api/v1/register/{registration_id}

    ```

    ```python
        #python
        import requests
        import json

        header = {'Content-Type': 'application/json'}

        body = {
                   "approveCode": "22f2a019590595819dca81e3ae6f81f4a39bd0470103044f936f6dd971803a23",
                   "email": "zops_test_eneoooeeN@example.com",
                   "password": "123",
                   "firstName": "emre",
                   "lastName": "dönmezs"
        }

        req = requests.put("https://api_baseurl/api/v1/register/{registration_id}",
                                        header=header, data=json.dumps(body))
    ```
    #### Response:
    202 Accepted:
    ```json

        {
        "meta": {
                "params": {
                            "indent": 0
                            }
                },
        "content": {
                    "id": "90c4cc8b11ab49a58ecb4b799faa8979",
                    "token": asdaskdh2uhehdasdhaksd,
                    "email": "zops_test_eneoooeeN@example.com",
                    "firstName": "emre",
                    "lastName": "dönmezs"
                    }
        }
    ```
    > Warning
    >
    > In order to obtain the token, after approving the account it is necessary to be logged in. The
    > response of the login request will include the token.

    #### Possible Errors
    - __Not Found__: Request invalid registration id.
    - __Not Found__: Request invalid approve code

    """

    serializer = RegisterSingleSerializer()

    def __repr__(self):
        return "Account Update with Approve Code"

    def resource_name(self):
        return "RegisterSingleResource"

    @require_roles(roles=[ERoles.anonym])
    def update(self, params, meta, **kwargs):
        registration_id = kwargs['registration_id']
        validated = kwargs['validated']
        hashed_password = data_hashing(validated['password'])

        account = self.db.get(Account, is_active=False, _id=registration_id)
        if account is None:
            raise HTTPNotFound(description="The account does not exist by given registration_id or already activated.")

        if account.approve_code == validated['approve_code']:
            admin = User(email=validated['email'], password=hashed_password, role=ERoles.admin,
                         first_name=validated['first_name'], last_name=validated['last_name'], account_id=account.id)

            account.is_active = True
            self.db.session.add(admin)
            token_payload = create_auth_token_payload(admin.id, role=admin.role, account_id=admin.account_id)
            token = encode_jwt_token(token_payload)
            add_user_token(admin.id, token)
            return {
                "token": token,
                "id": admin.id,
                "email": admin.email,
                "first_name": admin.first_name,
                "last_name": admin.last_name
            }
        else:
            raise HTTPConflict(description="Approve code does not match.")

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ApproveCodeResource(SaasBase, ListCreateAPI):
    """

    Allows to resend approve code

    ####### Code Example:

    #### POST
    Resend account approve code
    ### Request:

    ```bash
        #bash
        curl \\
             --request POST                             \\
             --header "Content-Type: application/json" \\
             --body "{                                                                                      \\
                   \"email\": \"zops_test_eneoooeeN@example.com\",                                          \\
             }"                                                                                             \\
             https://api_baseurl/api/v1/register/approve-code

    ```

    ```python
        #python
        import requests
        import json

        header = {'Content-Type': 'application/json'}

        body = {
                   "email": "zops_test_eneoooeeN@example.com",
        }

        req = requests.post("https://api_baseurl/api/v1/register/approve-code",
                                        header=header, data=json.dumps(body))
    ```
    #### Response:
    202 Accepted:
    ```json

        {
        "meta": {
                "params": {
                            "indent": 0
                            }
                }
        }
    ```

    #### Possible Errors
    - __Not Found__: These email address does not exist
    - __Failed Dependency__ :An Error occur on 3rd part service. Please retry after a few minutes.

    """

    serializer = ApproveCodeSerializer()
    testing = BoolParam("Testing mode parameter.", default="False")

    def __repr__(self):
        return "Approve Code Resend"

    def resource_name(self):
        return "ApproveCodeResource"

    @require_roles(roles=[ERoles.anonym])
    def create(self, params, meta, **kwargs):
        email = kwargs['validated']['email']
        testing = params.get('testing')
        account = self.db.get_account_with_email(email)
        if account:
            new_approve_code = generate_token()
            account.approve_code = new_approve_code
            mail_response = send_account_approve_mail(new_approve_code, email, account.id, testing)
            email_object = Email(provider_mail_id=mail_response['id'], account_id=account.id,
                                 text=mail_response['text'], subject=mail_response['subject'], receiver=email,
                                 provider="MAILGUN", category="approve")
            self.db.session.add(email_object)
        else:
            raise HTTPNotFound(description="These email address does not exist")

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

