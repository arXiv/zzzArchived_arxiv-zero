"""Flask configuration."""

from typing import Optional
import warnings
from os import environ

APP_VERSION = "0.2.1"
"""Version of this application."""

NAMESPACE = environ.get('NAMESPACE')
"""Namespace in which this service is deployed; to qualify keys for secrets."""

APPLICATION_ROOT = environ.get('APPLICATION_ROOT', '/')
"""Path where application is deployed."""

SITE_URL_PREFIX = environ.get('APPLICATION_ROOT', '/')

# RELATIVE_STATIC_PATHS = True
RELATIVE_STATIC_PREFIX = environ.get('APPLICATION_ROOT', '')

LOGLEVEL = int(environ.get('LOGLEVEL', '20'))
"""
Logging verbosity.

See `https://docs.python.org/3/library/logging.html#levels`_.
"""

JWT_SECRET = environ.get('JWT_SECRET')
"""Secret key for signing + verifying authentication JWTs."""

CSRF_SECRET = environ.get('FLASK_SECRET', 'csrfbarsecret')
"""Secret used for generating CSRF tokens."""

if not JWT_SECRET:
    warnings.warn('JWT_SECRET is not set; authn/z may not work correctly!')


WAIT_FOR_SERVICES = bool(int(environ.get('WAIT_FOR_SERVICES', '0')))
"""Disable/enable waiting for upstream services to be available on startup."""
if not WAIT_FOR_SERVICES:
    warnings.warn('Awaiting upstream services is disabled; this should'
                  ' probably be enabled in production.')

WAIT_ON_STARTUP = int(environ.get('WAIT_ON_STARTUP', '0'))
"""Number of seconds to wait before checking upstream services on startup."""

ENABLE_CALLBACKS = bool(int(environ.get('ENABLE_CALLBACKS', '1')))
"""Enable/disable the :func:`Event.bind` feature."""

SESSION_COOKIE_NAME = 'submission_ui_session'
"""Cookie used to store submission-related information."""


# --- FLASK CONFIGURATION ---

DEBUG = bool(int(environ.get('DEBUG', '0')))
"""enable/disable debug mode"""

TESTING = bool(int(environ.get('TESTING', '0')))
"""enable/disable testing mode"""

SECRET_KEY = environ.get('FLASK_SECRET', 'fooflasksecret')
"""Flask secret key."""

PROPAGATE_EXCEPTIONS = \
    True if bool(int(environ.get('PROPAGATE_EXCEPTIONS', '0'))) else None
"""
explicitly enable or disable the propagation of exceptions. If not set or
explicitly set to None this is implicitly true if either TESTING or DEBUG is
true.
"""

PRESERVE_CONTEXT_ON_EXCEPTION: Optional[bool] = None
"""
By default if the application is in debug mode the request context is not
popped on exceptions to enable debuggers to introspect the data. This can be
disabled by this key. You can also use this setting to force-enable it for non
debug execution which might be useful to debug production applications (but
also very risky).
"""
if bool(int(environ.get('PRESERVE_CONTEXT_ON_EXCEPTION', '0'))):
    PRESERVE_CONTEXT_ON_EXCEPTION = True


USE_X_SENDFILE = bool(int(environ.get('USE_X_SENDFILE', '0')))
"""Enable/disable x-sendfile"""

LOGGER_NAME = environ.get('LOGGER_NAME', 'search')
"""The name of the logger."""

LOGGER_HANDLER_POLICY = environ.get('LOGGER_HANDLER_POLICY', 'debug')
"""
the policy of the default logging handler. The default is 'always' which means
that the default logging handler is always active. 'debug' will only activate
logging in debug mode, 'production' will only log in production and 'never'
disables it entirely.
"""

SERVER_NAME = None  # "foohost:8000"   #environ.get('SERVER_NAME', None)
"""
the name and port number of the server. Required for subdomain support
(e.g.: 'myapp.dev:5000') Note that localhost does not support subdomains so
setting this to 'localhost' does not help. Setting a SERVER_NAME also by
default enables URL generation without a request context but with an
application context.
"""


# --- DATABASE CONFIGURATION ---

SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///')
"""Full database URI."""

SQLALCHEMY_TRACK_MODIFICATIONS = False
"""Track modifications feature should always be disabled."""


# Integration with the foo service.
FOO_HOST = environ.get('FOO_SERVICE_HOST', 'arxiv.org')
"""Hostname or addreess of the foo service."""

FOO_PORT = environ.get('FOO_SERVICE_PORT', '443')
"""Port for the foo service."""

FOO_PROTO = environ.get(f'FOO_PORT_{FOO_PORT}_PROTO',
                             environ.get('FOO_PROTO', 'https'))
"""Protocol for the foo service."""

FOO_PATH = environ.get('FOO_PATH', '')
"""Path at which the foo service is deployed."""

FOO_ENDPOINT = environ.get(
    'FOO_ENDPOINT',
    '%s://%s:%s/%s' % (FOO_PROTO, FOO_HOST, FOO_PORT,
                       FOO_PATH)
)
"""
Full URL to the root foo service API endpoint.

If not explicitly provided, this is composed from :const:`FOO_HOST`,
:const:`FOO_PORT`, :const:`FOO_PROTO`, and :const:`FOO_PATH`.
"""

FOO_STATUS_TIMEOUT = float(environ.get('FOO_STATUS_TIMEOUT', 1.0))

FOO_VERIFY = bool(int(environ.get('FOO_VERIFY', '1')))
"""Enable/disable SSL certificate verification for foo service."""

if FOO_PROTO == 'https' and not FOO_VERIFY:
    warnings.warn('Certificate verification for foo is disabled; this'
                  ' should not be disabled in production.')


# --- EXTERNAL URL CONFIG --- 

EXTERNAL_URL_SCHEME = environ.get('EXTERNAL_URL_SCHEME', 'https')
BASE_SERVER = environ.get('BASE_SERVER', 'arxiv.org')

URLS = [
    ("help_license", "/help/license", BASE_SERVER),
    ("help_third_party_submission", "/help/third_party_submission",
     BASE_SERVER),
    ("help_cross", "/help/cross", BASE_SERVER),
    ("help_submit", "/help/submit", BASE_SERVER),
    ("help_ancillary_files", "/help/ancillary_files", BASE_SERVER),
    ("help_texlive", "/help/faq/texlive", BASE_SERVER),
    ("help_whytex", "/help/faq/whytex", BASE_SERVER),
    ("help_default_packages", "/help/submit_tex#wegotem", BASE_SERVER),
    ("help_submit_tex", "/help/submit_tex", BASE_SERVER),
    ("help_submit_pdf", "/help/submit_pdf", BASE_SERVER),
    ("help_submit_ps", "/help/submit_ps", BASE_SERVER),
    ("help_submit_html", "/help/submit_html", BASE_SERVER),
    ("help_submit_sizes", "/help/sizes", BASE_SERVER),
    ("help_metadata", "/help/prep", BASE_SERVER),
    ("help_jref", "/help/jref", BASE_SERVER),
    ("help_withdraw", "/help/withdraw", BASE_SERVER),
    ("help_replace", "/help/replace", BASE_SERVER),
    ("help_endorse", "/help/endorsement", BASE_SERVER),
    ("clickthrough", "/ct?url=<url>&v=<v>", BASE_SERVER),
    ("help_endorse", "/help/endorsement", BASE_SERVER),
    ("help_replace", "/help/replace", BASE_SERVER),
    ("help_version", "/help/replace#versions", BASE_SERVER),
    ("help_email", "/help/email-protection", BASE_SERVER),
    ("help_author", "/help/prep#author", BASE_SERVER),
    ("help_mistakes", "/help/faq/mistakes", BASE_SERVER),
    ("help_texprobs", "/help/faq/texprobs", BASE_SERVER),
    ("login", "/user/login", BASE_SERVER)
]
"""
URLs for external services, for use with :func:`flask.url_for`.
This subset of URLs is common only within submit, for now - maybe move to base
if these pages seem relevant to other services.

For details, see :mod:`arxiv.base.urls`.
"""

AUTH_UPDATED_SESSION_REF = False
"""
Authn/z info is at ``request.session`` instead of ``request.auth``.

See `https://arxiv-org.atlassian.net/browse/ARXIVNG-2186`_.
"""

# --- AWS CONFIGURATION ---

AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID', 'nope')
"""
Access key for requests to AWS services.

If :const:`VAULT_ENABLED` is ``True``, this will be overwritten.
"""

AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY', 'nope')
"""
Secret auth key for requests to AWS services.

If :const:`VAULT_ENABLED` is ``True``, this will be overwritten.
"""

AWS_REGION = environ.get('AWS_REGION', 'us-east-1')
"""Default region for calling AWS services."""


# --- KINESIS CONFIGURATION ---

KINESIS_STREAM = environ.get("KINESIS_STREAM", "SubmissionEvents")
"""Name of the stream on which to produce and consume events."""

KINESIS_SHARD_ID = environ.get("KINESIS_SHARD_ID", "0")
"""
Shard ID for this agent instance.

There must only be one agent process running per shard.
"""

KINESIS_START_TYPE = environ.get("KINESIS_START_TYPE", "TRIM_HORIZON")
"""Start type to use when no checkpoint is available."""

KINESIS_ENDPOINT = environ.get("KINESIS_ENDPOINT", None)
"""
Alternate endpoint for connecting to Kinesis.

If ``None``, uses the boto3 defaults for the :const:`AWS_REGION`. This is here
mainly to support development with localstack or other mocking frameworks.
"""

KINESIS_VERIFY = bool(int(environ.get("KINESIS_VERIFY", "1")))
"""
Enable/disable TLS certificate verification when connecting to Kinesis.

This is here support development with localstack or other mocking frameworks.
"""

if not KINESIS_VERIFY:
    warnings.warn('Certificate verification for Kinesis is disabled; this'
                  ' should not be disabled in production.')


# --- VAULT INTEGRATION CONFIGURATION ---

VAULT_ENABLED = bool(int(environ.get('VAULT_ENABLED', '0')))
"""Enable/disable secret retrieval from Vault."""

KUBE_TOKEN = environ.get('KUBE_TOKEN', 'fookubetoken')
"""Service account token for authenticating with Vault. May be a file path."""

VAULT_HOST = environ.get('VAULT_HOST', 'foovaulthost')
"""Vault hostname/address."""

VAULT_PORT = environ.get('VAULT_PORT', '1234')
"""Vault API port."""

VAULT_ROLE = environ.get('VAULT_ROLE', 'submission-ui')
"""Vault role linked to this application's service account."""

VAULT_CERT = environ.get('VAULT_CERT')
"""Path to CA certificate for TLS verification when talking to Vault."""

VAULT_SCHEME = environ.get('VAULT_SCHEME', 'https')
"""Default is ``https``."""

NS_AFFIX = '' if NAMESPACE == 'production' else f'-{NAMESPACE}'
VAULT_REQUESTS = [
    {'type': 'generic',
     'name': 'JWT_SECRET',
     'mount_point': f'secret{NS_AFFIX}/',
     'path': 'jwt',
     'key': 'jwt-secret',
     'minimum_ttl': 3600},
    {'type': 'aws',
     'name': 'AWS_S3_CREDENTIAL',
     'mount_point': f'aws{NS_AFFIX}/',
     'role': environ.get('VAULT_CREDENTIAL')},
    {'type': 'generic',
     'name': 'SQLALCHEMY_DATABASE_URI',
     'mount_point': f'secret{NS_AFFIX}/',
     'path': 'beta-mysql',
     'key': 'uri',
     'minimum_ttl': 360000},
]
"""Requests for Vault secrets."""
