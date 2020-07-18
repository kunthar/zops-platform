from zopsm.lib.credis import ZRedis
from zopsm.lib import sd_redis

cache = ZRedis(host=sd_redis.watch_redis(single=True)[0],
               password='quohte2AaekipheeDo3E8iWaLieT2iesGoo2ejikIepe4kooooQu6aDauixaiMe0uXaer0Lutie3exnoooR6ahcuXeet5leicoo7Tiehcsa3Tha5whai1OhGAj6yag7AeekoT7aethohJai1Iefie8mu',
               db=1)
"""
"Tenants:123:Projects:456:Subscriber:123456:Contacts": {"subscriberId1","subscriberId3","subscriberId2",},

"RefreshTokens:{temp_token}": {"tenant:"123", "account":"007", "project":"456", "service":"789", "user":"user_id"}
"""

users = ["testUser0", "testUser1", "testUser2", "testUser3", "testUser4", "testUser5", "testUser6",
         "testUser7", "testUser8", "testUser9"]

possible_channels = ["testChannel1", "testChannel2", "testChannel3"]

contact_lists = {
    "testUser0": ["testUser4", "testUser8", "testUser9"],
    "testUser1": [],
    "testUser2": ["testUser3", "testUser5", "testUser7"],
    "testUser3": ["testUser2"],
    "testUser4": ["testUser0", "testUser6"],
    "testUser5": ["testUser2", "testUser6", "testUser9"],
    "testUser6": ["testUser4", "testUser5"],
    "testUser7": ["testUser2", "testUser8", "testUser9"],
    "testUser8": ["testUser0", "testUser7", "testUser9"],
    "testUser9": ["testUser0", "testUser5", "testUser7", "testUser8"],
}

channel_lists = {
    "testUser0": ["testChannel1", "testChannel2", "testChannel3"],
    "testUser1": ["testChannel2", "testChannel3"],
    "testUser2": ["testChannel3"],
    "testUser3": ["testChannel2", "testChannel3"],
    "testUser4": ["testChannel1", "testChannel3"],
    "testUser5": ["testChannel3"],
    "testUser6": ["testChannel1", "testChannel3"],
    "testUser7": ["testChannel1", "testChannel2", "testChannel3"],
    "testUser8": ["testChannel1", "testChannel2", "testChannel3"],
    "testUser9": ["testChannel2", "testChannel3"],
}

channel_subscribers_lists = {
    "testChannel1": ["testUser0", "testUser4", "testUser6", "testUser7", "testUser8"],
    "testChannel2": ["testUser0", "testUser1", "testUser3", "testUser7", "testUser8", "testUser9"],
    "testChannel3": ["testUser0", "testUser1", "testUser2", "testUser3", "testUser4", "testUser5",
                     "testUser6", "testUser7", "testUser8", "testUser9"],
}

tenant = "TestTenant1"
account = "TestAccount1"
project = "TestProject1"
service = "TestService1"

for u in users:
    refresh_token_key = "RefreshTokens:{}".format(u)
    refresh_token_value = {
        "tenant_id": tenant,
        "account_id": account,
        "project_id": project,
        "service_id": service,
        "accessToken": u,
        "user": u
    }
    cache.hmset(refresh_token_key, refresh_token_value)
    access_token_key = "AccessTokens:{}".format(u)
    access_token_value = {
        "tenant_id": "TestTenant1",
        "account_id": "TestAccount1",
        "project_id": "TestProject1",
        "service_id": "TestService1",
        "user": u
    }
    cache.hmset(access_token_key, access_token_value)
    contacts_key = "Tenants:{}:Accounts:{}:Projects:{}:Subscriber:{}:Contacts".format(
        tenant, account, project, u
    )
    contacts = contact_lists[u]
    if contacts:
        cache.sadd(contacts_key, *contacts)

    channels_key = "Tenants:{}:Accounts:{}:Projects:{}:Subscriber:{}:Channels".format(
        tenant, account, project, u
    )
    channels = channel_lists[u]
    if channels:
        cache.sadd(channels_key, *channels)

for c in possible_channels:
    subscribers_key = "Tenants:{}:Accounts:{}:Projects:{}:Channels:{}:Subscribers".format(
        tenant, account, project, c
    )
    subscribers = channel_subscribers_lists[c]
    if subscribers:
        cache.sadd(subscribers_key, *subscribers)

cache.sadd(
    "Tenants:{}:Accounts:{}:Projects:{}:Services:{}:OnlineSubscribers".format(
        tenant, account, project, service),
    *users[5:]
)

