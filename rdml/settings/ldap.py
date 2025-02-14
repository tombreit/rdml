# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

# ldap/ad auth
# see: http://django-auth-ldap.readthedocs.io/en/latest/index.html

import logging
import ldap

from django_auth_ldap.config import (
    LDAPSearch,
    LDAPSearchUnion,
    ActiveDirectoryGroupType,
    LDAPGroupQuery,
)

from .base import env


# Logging stanza
# Comment out when not needed:
logger = logging.getLogger("django_auth_ldap")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


AUTH_LDAP_SERVER_URI = env.str("AUTH_LDAP_SERVER_URI")
AUTH_LDAP_BIND_DN = env.str("AUTH_LDAP_BIND_DN")
AUTH_LDAP_BIND_PASSWORD = env.str("AUTH_LDAP_BIND_PASSWORD")

AUTH_LDAP_GLOBAL_OPTIONS = {
    # ldap.OPT_PROTOCOL_VERSION: 3,
    # ldap.OPT_REFERRALS: 0,
    # ldap.OPT_X_TLS_CACERTFILE: '/path/to/pemfile',
}

# First check LDAPBackend, than ModelBackend
AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_CACHE_TIMEOUT = 60 * 60
# https://django-auth-ldap.readthedocs.io/en/latest/reference.html#auth-ldap-cache-timeout
AUTH_LDAP_CACHE_TIMEOUT = 0
AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn", "email": "mail"}

AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
    LDAPSearch(
        f"{env.str('AUTH_LDAP_USERS_DN')}",
        ldap.SCOPE_SUBTREE,
        "(mail=%(user)s)",
    ),
)

AUTH_LDAP_GROUP_SEARCH = LDAPSearchUnion(
    LDAPSearch(f"{env.str('AUTH_LDAP_USERS_DN')}", ldap.SCOPE_SUBTREE, "(objectClass=group)"),
)

# https://django-auth-ldap.readthedocs.io/en/latest/groups.html#limiting-access
AUTH_LDAP_MIRROR_GROUPS = env.list("AUTH_LDAP_MIRROR_GROUPS_LIST")

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_active": (
        LDAPGroupQuery(env.str("AUTH_LDAP_GROUP_SUPERUSERS")) | LDAPGroupQuery(env.str("AUTH_LDAP_GROUP_STAFF"))
    ),
    "is_staff": (
        LDAPGroupQuery(env.str("AUTH_LDAP_GROUP_SUPERUSERS")) | LDAPGroupQuery(env.str("AUTH_LDAP_GROUP_STAFF"))
    ),
    "is_superuser": (LDAPGroupQuery(env.str("AUTH_LDAP_GROUP_SUPERUSERS"))),
}

if env.bool("DEBUG"):
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    ldap.set_option(ldap.OPT_DEBUG_LEVEL, 255)
