# -*-  coding: utf-8 -*-
import os
import json

# 2017-08-20T08:54:56.750Z00:00
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ00:00"

# testing or production mode specifier
WORKING_ENVIRONMENT = os.getenv('WORKING_ENVIRONMENT', 'zopsm')

# virtual host
VIRTUAL_HOST = os.getenv('RABBIT_VHOST', 'zopsm')


# Redis keys and prefixes

"""
To make an efficient memory usage on Redis, it is used the following key map for the keys and 
prefixes:

    AccTok: AccessTokens
    
    BanCh: BannedChannels
    BanSub: BannedSubscribers
    
    C: Contacts
    Ch: Channels
    CRI: Contact Requests In
    CRO: Contact Requests Out
    
    Dyn: Prefix for dynamically generated keys on the Redis itself and guaranteed to be volatile 
    with a short expire time. 
    
    Inv: Invites
    Invee: Invitees
    
    JR: JoinRequests
    
    Man: Managers
    
    OnSub: OnlineSubscribers
    Own: Owners
    
    P: Projects
    PGSK: Push Google Server API Key
    PGPN: Push Google Project Number (Sender ID)
    PAPC: Push APNS iOS Push Certificate (ascii text)
    
    RefTok: RefreshTokens
    
    S: Services
    St: Statuses
    Sub: Subscribers
    
    SUT: Saas User Token
    
    TokensKeys: TokensKeys
 
"""

# Online Subscribers
CACHE_ONLINE_SUBSCRIBERS = "P:{project_id}:S:{service}:OnSub"

# Idle Subscribers
CACHE_IDLE_SUBSCRIBERS = "P:{project_id}:S:{service}:IdleSub"

# Subscriber
CACHE_SUBSCRIBER_EXPIRE = 60 * 60 * 24 * 3  # 3 days
CACHE_SUBSCRIBERS = "P:{project_id}:S:{service}:Sub:{subscriber_id}"

# Status of a subscriber
CACHE_STATUS = "P:{project_id}:S:{service}:St:{subscriber_id}"
CACHE_STATUS_EXPIRE = 300  # 5 minutes

# Contacts of a subscriber
CACHE_CONTACTS = "P:{project_id}:S:{service}:Sub:{subscriber_id}:C"

# Channels of a subscriber
CACHE_SUBSCRIBER_CHANNELS = "P:{project_id}:S:{service}:Sub:{subscriber_id}:Ch"

# Channels of a subscriber
CACHE_SUBSCRIBER_CHANNELS_DATA = "P:{project_id}:S:{service}:Sub:{subscriber_id}:Ch:{channel_id}"
# Contacts of a subscriber
CACHE_SUBSCRIBER_CONTACTS_DATA = "P:{project_id}:S:{service}:Sub:{subscriber_id}:C:{contact_id}"

# Banned Channels of a subscriber
CACHE_SUBSCRIBER_BANNED_CHANNELS = "P:{project_id}:S:{service}:Sub:{subscriber_id}:BanCh"

# Banned Subscribers of a subscriber
CACHE_SUBSCRIBER_BANNED_SUBSCRIBERS = "P:{project_id}:S:{service}:Sub:{subscriber_id}:BanSub"

# Channel Invites of a subscriber
CACHE_SUBSCRIBER_CHANNEL_INVITES = "P:{project_id}:S:{service}:Sub:{subscriber_id}:Inv"

# Channel Join Requests of a subscriber
CACHE_SUBSCRIBER_CHANNEL_JOIN_REQUESTS = "P:{project_id}:S:{service}:Sub:{subscriber_id}:JR"

# Incoming Contact Requests sent to subscriber
CACHE_SUBSCRIBER_CONTACT_REQUESTS_IN = "P:{project_id}:S:{service}:Sub:{subscriber_id}:CRI"

# Contact Requests sent by subscriber
CACHE_SUBSCRIBER_CONTACT_REQUESTS_OUT = "P:{project_id}:S:{service}:Sub:{subscriber_id}:CRO"

# Channel
CACHE_CHANNEL_EXPIRE = 60 * 60 * 24 * 3  # 3 days
CACHE_CHANNELS = "P:{project_id}:S:{service}:Ch:{channel_id}"
# Channel Managers
CACHE_CHANNEL_MANAGERS = "P:{project_id}:S:{service}:Ch:{channel_id}:Man"
# Channel Subscribers
CACHE_CHANNEL_SUBSCRIBERS = "P:{project_id}:S:{service}:Ch:{channel_id}:Sub"
# Channel Owners
CACHE_CHANNEL_OWNERS = "P:{project_id}:S:{service}:Ch:{channel_id}:Own"
# Channel Banned Subscribers
CACHE_CHANNEL_BANNED_SUBSCRIBERS = "P:{project_id}:S:{service}:Ch:{channel_id}:BanSub"
# Channel Invitees
CACHE_CHANNEL_INVITEES = "P:{project_id}:S:{service}:Ch:{channel_id}:Invee"
# Channel Join Requests
CACHE_CHANNEL_JOIN_REQUESTS = "P:{project_id}:S:{service}:Ch:{channel_id}:JR"


# token expire time
CACHE_REFRESH_TOKEN_EXPIRE_IN = 60   # 60 second expire time for refresh tokens(produced in saas)
CACHE_ACCESS_TOKEN_EXPIRES_IN = 60 * 60 * 3  # 3 hours expire time for access tokens

# Tokens Keys

CACHE_TOKENS_KEYS = "TokensKeys"

# Token List
CACHE_SERVICE_TOKEN_LIST = "TokenList:P:{project_id}:S:{service}"

# Access Tokens

CACHE_ACCESS_TOKEN = "P:{project_id}:S:{service}:AccTok:{token}"
CACHE_ACCESS_TOKENS = "P:{project_id}:S:{service}:AccTok"

# Refresh Tokens

CACHE_REFRESH_TOKEN = "P:{project_id}:S:{service}:RefTok:{token}"
CACHE_REFRESH_TOKENS = "P:{project_id}:S:{service}:RefTok"

# project services tokens
ADMIN_TOKENS = "AdminTokenKeys"
PROJECT_SERVICES_ADMIN_TOKEN = "P:{project_id}  :AdminTok"

# Push API Keys and Certs
CACHE_PUSH_GOOGLE_API_KEY = "P:{project_id}:PGSK"
CACHE_PUSH_GOOGLE_PROJECT_NUMBER = "P:{project_id}:PGPN"
CACHE_PUSH_APNS_CERT = "P:{project_id}:PAPC"

# Saas User Authorization Token
CACHE_SAAS_AUTH_TOKEN = "SUT:{user_id}"

# Saas Reset Password Token
CACHE_SAAS_RESET_PASSWORD_KEY = "ResetPasswordKeys"

# Vault Paths

# APNS Certificate File Path
"""
APNS:

    path: {project_id}/apns
    data: {
        "cert_file": "CERT_FILE_CONTENT" 
    }
    
FCM: 
    path: {project_id}/fcm
    data: {
        "api_key": "API_KEY",
        "project_number": "PROJECT_NUMBER" 
    }

"""
working_path = os.getenv('VAULT_WORKING_PATH')
VAULT_PUSH_APNS_PATH = "{}/{project_id}/apns".format(working_path, project_id="{project_id}")
VAULT_PUSH_FCM_PATH = "{}/{project_id}/fcm".format(working_path, project_id="{project_id}")

# Mail Gun Variables for sending email
ZOPSM_APPROVE_URL = "zops.io/approve"
ZOPSM_FORGOT_PASSWORD_URL = "zops.io/forgot-password"

MAIL_GUN_URL = "https://api.mailgun.net/v3/mg.zops.io/messages"
MAIL_GUN_API_KEY = "key-4adda06f27f150e0d920632cdbe5b275"
ADDRESS_FROM = "ZOPSM <noreply@mg.zops.io>"

APPROVE_CODE_MAIL_TEXT = "Approve Url: {url}?{url_params}"
APPROVE_CODE_MAIL_SUBJECT = "ZOPSM Registration Approve Code"

RESET_PASSWORD_MAIL_TEXT = "Reset Password: {url}?{url_params}"
RESET_PASSWORD_MAIL_SUBJECT = "ZOPSM Reset Password"

ACCOUNT_LIMIT = {
    "project_limit": 5,
    "user_limit": 1000,
    "message_limit": {
        "roc": 10000,
        "push": 1000,
        "sms": 0
    }
}

account_limit = os.getenv('ACCOUNT_LIMIT')

if account_limit:
    ACCOUNT_LIMIT = json.loads(account_limit)
