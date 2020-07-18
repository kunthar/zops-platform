import falcon
import consul
import os
from zopsm.lib.sd_consul import consul_client, EnvironmentVariableNotFound
from zopsm.saas.auth import AuthorizationMiddleware
from zopsm.lib.rest.response_logger import ResponseLoggerMiddleware
from zopsm.lib.rest.session_manager import DatabaseSessionManager
from zopsm.saas.resources.account import AccountResource
from zopsm.saas.resources.login import LoginResource, LogoutResource, ForgotPasswordResource, ResetPasswordResource
from zopsm.saas.resources.register import RegisterResource, RegisterSingleResource, ApproveCodeResource
from zopsm.saas.resources.admin import AdminResource, AdminSingleResource
from zopsm.saas.resources.billing import BillingResource, BillingSingleResource
from zopsm.saas.resources.developer import DeveloperResource, DeveloperSingleResource
from zopsm.saas.resources.project import ProjectResource, ProjectSingleResource, ProjectSecretResource, ProjectServicesAdminTokenResource
from zopsm.saas.resources.service import ServiceCatalogResource, ServiceResource, ServiceSingleResource
from zopsm.saas.resources.service import ServiceEventResource
from zopsm.saas.resources.me import MeResource
from zopsm.saas.resources.email_tracking import EmailTrackingResource
from zopsm.saas.resources.log_notifier import LogNotifierResource, LogTrackingResource
from zopsm.saas.resources.consumer import ConsumerResource, ProjectConsumerDeleteResource
from zopsm.saas.resources.consumer import ProjectConsumerCreateResource, ConsumerTokenCreate, ConsumerTokenDelete
from zopsm.lib.rest.resource import ResourceListResource, Ping
from zopsm.lib.settings import WORKING_ENVIRONMENT

container_name = os.getenv('CONTAINER_NAME', 'saas')
container_port = int(os.getenv('CONTAINER_PORT', 10000))

host_ipv4 = os.getenv('DOCKER_HOST_IPV4')
if host_ipv4 is None:
    raise EnvironmentVariableNotFound('DOCKER_HOST_IPV4 should not be empty.')

if WORKING_ENVIRONMENT in ["zopsm", "develop"]:
    # Consul service and check registration
    check = consul.Check.http(
        url=f'http://{host_ipv4}:{container_port}/api/v1/ping',
        timeout='1s',
        interval='10s',
        deregister='2m')

    consul_client.agent.service.register(
        name='saas',
        service_id=f'{container_name}',
        address=f'{host_ipv4}',
        port=int(container_port),
        check=check)

app = application = falcon.API(
    middleware=[
        AuthorizationMiddleware(),
        DatabaseSessionManager(),
        ResponseLoggerMiddleware(),
    ])

rev_path = '/api/v1'

endpoints = {
    # Login resource post session
    rev_path + '/session': LoginResource(),
    # Logout resource delete session if others parameters true users all token deleted
    rev_path + '/session/logout': LogoutResource(),

    # Forgot password resource. User reset password via these resource
    rev_path + '/forgot-password': ForgotPasswordResource(),
    rev_path + '/reset-password': ResetPasswordResource(),

    # Account update and delete resource
    rev_path + '/account': AccountResource(),

    # Account registration and account manager initialization.
    rev_path + '/register': RegisterResource(),
    rev_path + '/register/{registration_id}': RegisterSingleResource(),

    rev_path + '/register/approve-code': ApproveCodeResource(),

    # Account admin CRUD
    rev_path + '/admins': AdminResource(),
    rev_path + '/admins/{admin_id}': AdminSingleResource(),

    # Account billing CRUD
    rev_path + '/billings': BillingResource(),
    rev_path + '/billings/{billing_id}': BillingSingleResource(),

    # Account developer CRUD
    rev_path + '/developers': DeveloperResource(),
    rev_path + '/developers/{developer_id}': DeveloperSingleResource(),

    # get user information
    rev_path + '/me': MeResource(),

    # Account project CRUD and RefreshToken
    rev_path + '/projects': ProjectResource(),
    rev_path + '/projects/{project_id}': ProjectSingleResource(),
    rev_path + '/projects/{project_id}/api': ProjectSecretResource(),
    rev_path + '/projects/{project_id}/services-token': ProjectServicesAdminTokenResource(),

    # ServiceCatalog Create and List.
    rev_path + '/services': ServiceCatalogResource(),
    rev_path + '/service-event': ServiceEventResource(),

    # Service CRUD, attach and deattach process on account project.
    rev_path + '/projects/{project_id}/services': ServiceResource(),
    rev_path + '/projects/{project_id}/services/{service_catalog_code}': ServiceSingleResource(),

    # Consumer CRUD on Account.
    rev_path + '/consumers': ConsumerResource(),

    # De/Attach consumer to Project single and bulk
    rev_path + '/projects/{project_id}/consumers/{consumer_id}': ProjectConsumerDeleteResource(),
    rev_path + '/projects/{project_id}/consumers': ProjectConsumerCreateResource(),
    # api.add_route(rev_path + '/projects/{project_id}/consumer', ProjectConsumerBulkResource())

    # Not checked the code
    # rev_path + '/tenants': TenantResource(),
    # rev_path + '/tenants/{tenant_id}': TenantResourceSingle(),

    # Create and Delete ConsumerToken
    rev_path + '/consumer-tokens/': ConsumerTokenCreate(),
    rev_path + '/consumer-tokens/{token_id}/projects/{project_id}/services/{service_catalog_code}': ConsumerTokenDelete(),
    # email-tracking for managers
    rev_path + '/email-tracking': EmailTrackingResource(),
    # log-notifier resource
    rev_path + '/log-notifier': LogNotifierResource(),
    # log tracking resource. only manager can use these resource
    rev_path + '/log-tracking': LogTrackingResource(),

    # Ping
    rev_path + '/ping': Ping(),

}

for uri, endpoint in endpoints.items():
    app.add_route(uri, endpoint)

app.add_route('/', ResourceListResource(endpoints))
