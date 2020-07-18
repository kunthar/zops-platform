from falcon.errors import HTTPMethodNotAllowed, HTTPNotFound
from graceful.fields import StringField
from graceful.parameters import BoolParam
from graceful.resources.generic import RetrieveUpdateDeleteAPI, ListCreateAPI, RetrieveUpdateAPI
from zopsm.saas.auth import require_roles
from zopsm.saas.models import ERoles, User, Email
from zopsm.saas.validators import email_validator
from zopsm.saas.resources.saas_base import SaasBase
from zopsm.saas.utility import add_user_token
from zopsm.lib.rest.serializers import ZopsBaseSerializer
from zopsm.saas.utility import encode_jwt_token, decode_jwt_token
from zopsm.saas.utility import create_reset_password_payload, create_auth_token_payload
from zopsm.saas.utility import data_hashing
from zopsm.saas.utility import remove_user_tokens
from zopsm.saas.utility import remove_user_token
from zopsm.saas.utility import send_reset_password_mail
from zopsm.saas.utility import add_reset_password_token
from zopsm.saas.utility import remove_reset_password_token


class LoginSerializer(ZopsBaseSerializer):
    token = StringField("Access token.", read_only=True)
    email = StringField("Email for user.Max length 70 Character", write_only=True, validators=[email_validator])
    password = StringField("Password for user.Max length 128 Character", write_only=True)


class LogoutSerializer(ZopsBaseSerializer):
    token = StringField("Access token", read_only=True)


class ForgotPasswordSerializer(ZopsBaseSerializer):
    email = StringField("Email for user.Max length 70 Character", write_only=True, validators=[email_validator])


class ResetPasswordSerializer(ZopsBaseSerializer):
    resetToken = StringField("Forgot Password Token", write_only=True, source="reset_token")
    password = StringField("New password for user. Max length 128 Character", write_only=True)


class LoginResource(SaasBase, ListCreateAPI):
    """
    Login Resource.

    #### Code Example:

    ### POST
    Login System with Email and Password.
    Return User_Id, Role and Token(Token used until logout )

    #### Request

        ```bash
            #bash
            curl \\
                 --request POST                             \\
                 --header "Content-Type: application/json"  \\
                 --body "{                                                             \\
                         \"email\": \"zops_test_eneoooeeN@example.com\",               \\
                         \"password\": \"123\"                                         \\
                 }"                                                                    \\
                 https://api_baseurl/api/v1/session
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json"
                      }

            body = {
                    "email": "zops_test_eneoooeeN@example.com",
                    "password": "123",
                    }

            req = requests.post("https://api_baseurl/api/v1/session",
                                            header=header, data=json.dumps(body))
        ```
        #### Response:
        ```json
            {
            "meta": {
                    "params": {
                                "indent": 0
                                }
                    },
            "content": {
                        "token": "asdljfsl394whefsudfo9sdfysdf"
                        }
            }
        ```

    """

    serializer = LoginSerializer()

    def __repr__(self):
        return "LoginResource"

    def resource_name(self):
        return "User Login"

    @require_roles(roles=[ERoles.anonym])
    def create(self, params, meta, **kwargs):
        validated = kwargs['validated']
        hashed_password = data_hashing(validated['password'])
        user = self.db.login(validated['email'], hashed_password)

        if user.role.name is "manager":
            token_payload = create_auth_token_payload(user.id, role=user.role, tenant_id=user.tenant_id)
            token = encode_jwt_token(token_payload)
        else:
            token_payload = create_auth_token_payload(user.id, role=user.role, account_id=user.account_id)
            token = encode_jwt_token(token_payload)
        add_user_token(user.id, token)

        return {
            "token": token
        }

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class LogoutResource(SaasBase, RetrieveUpdateDeleteAPI):
    """
    Logout resource.
    User logout and used token invalidated.(token is disposable)
    If "others" parameters is true then users all token deleted except that used this request

    #### Code Example:

    #### DELETE
    Logout User Account and Invalidate user token.
    #### Request:

        ```bash
            #bash
            curl \\
                 --request DELETE                                                        \\
                 --header "Content-Type: application/json"                               \\
                 --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"   \\
                 https://api_baseurl/api/v1/session/logout
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                      }
            req = requests.GET("https://api_baseurl/api/v1/session/logout,
                                            header=header)
        ```
        ##### Response:
        202 OK.
        ```json
            {
              "meta": {
                "params": {
                  "indent": 0
                }
              },
              "content": null
            }
        ```
    #### DELETE
    If "others" parameters is true then users all token deleted except that used this request
    #### Request:

        ```bash
            #bash
            curl \\
                 --request DELETE                                                       \\
                 --header "Content-Type: application/json"                              \\
                 --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"  \\
                 https://api_baseurl/api/v1/session/logout?others=True
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                      }
            req = requests.GET("https://api_baseurl/api/v1/session/logout?others=True,
                                            header=header)
        ```
        ##### Response:
        202 OK.
        ```json
            {
              "meta": {
                "params": {
                  "indent": 0
                }
              },
              "content": null
            }
        ```

    """
    serializer = LogoutSerializer()

    others = BoolParam("This parameter is user delete token parameter. If it is true users all token deleted",
                       default="False")

    def __repr__(self):
        return "User Logout and Invalidate All Tokens"

    def resource_name(self):
        return "LogoutResource"

    @require_roles(roles=[ERoles.admin, ERoles.developer, ERoles.billing])
    def delete(self, params, meta, **kwargs):
        others = params.get('others')
        payload = kwargs['token']
        user_id = payload['sub']

        token = encode_jwt_token(payload)
        remove_user_token(user_id, token)

        if others:
            remove_user_tokens(user_id)
            add_user_token(user_id, token)

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def update(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ForgotPasswordResource(SaasBase, ListCreateAPI):
    """
    Forgot Password Resource

    ### Code Examples:

        #### POST:
        Send reset password email. We send to reset link your email address. You can reset your password using these
        link in 5 hours
        #### Request:

        ```bash
            #bash
            curl \\
                 --request POST                                                             \\
                 --header "Content-Type: application/json"                                  \\
                 --header "AUTHORIZATION: eyJ0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"   \\
                 --body "{                                                              \\
                         \"email\": \"zops_test_eneoooeeN@example.com\",                \\
                 }"                                                                     \\
                 https://api_baseurl/api/v1/forgot-password
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                      }

            body = {
                    "email": "zops_test_eneoooeeN@example.com"
                    }

            req = requests.post("https://api_baseurl/api/v1/forgot-password",
                                            header=header, data=json.dumps(body))
        ```

        #### Response:
        201 Accepted:
        ```json
            {
            "meta": {
                    "params": {
                                "indent": 0
                                }
                    },
            }
        ```
        #### Possible Errors
        - __Not Found__
        - __Unauthorized__
        - __Failed Dependency__ :An Error occur on 3rd part service. Please retry after a few minutes.


    """

    serializer = ForgotPasswordSerializer()

    def __repr__(self):
        return "Forgot Password Resource"

    def resource_name(self):
        return "ForgotPasswordResource"

    @require_roles(roles=[ERoles.anonym])
    def create(self, params, meta, **kwargs):
        email = kwargs['validated']['email']
        user = self.db.get_object(User, email=email)

        token_payload = create_reset_password_payload(email)
        token = encode_jwt_token(token_payload)
        add_reset_password_token(token)

        mail_response = send_reset_password_mail(email, token)
        email_object = Email(provider_mail_id=mail_response['id'], account_id=user.account_id,
                             text=mail_response['text'], subject=mail_response['subject'], receiver=email,
                             provider="MAILGUN", category="reset_password")
        self.db.session.add(email_object)

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ResetPasswordResource(SaasBase, RetrieveUpdateAPI):
    """
    Reset Password Resource

    ### Code Examples:

        #### PUT:
        Reset Password with reset_token and new password
        #### Request:
        ```bash
            #bash
            curl \\
                 --request PUT                                                              \\
                 --header "Content-Type: application/json"                                  \\
                 --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"      \\
                 --body "{                                                             \\
                         \"password\": \"123\",                                        \\
                         \"resetToken\": \"sdfsdfsdf23423dasdasdasd\"                  \\
                 }" \\
                 https://api_baseurl/api/v1/reset-password
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                      }
            body = {
                    "password": "123",
                    "resetToken": "asdfsdfsdfsdfsdf234234"
                    }
            req = requests.put("https://api_baseurl/api/v1/reset-password",
                                            header=header, data=json.dumps(body))
        ```
        ##### Response:
        202 Accepted.
        ```json{
              "meta": {
                "params": {
                  "indent": 0
                }
              }
            }
        ```
        #### Possible Error
        - __Not Found_
        - __Invalid Params__
    """

    serializer = ResetPasswordSerializer()

    def __repr__(self):
        return "Reset Password Resource"

    def resource_name(self):
        return "ResetPasswordResource"

    @require_roles(roles=[ERoles.anonym])
    def update(self, params, meta, **kwargs):
        reset_token = kwargs['validated']['reset_token']
        password = kwargs['validated']['password']
        if not remove_reset_password_token(reset_token):
            raise HTTPNotFound(description="Invalid reset token")

        payload = decode_jwt_token(reset_token, "resetToken")
        user = self.db.get_object(User, email=payload['email'])
        hashed_password = data_hashing(password)
        user.password = hashed_password

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())
