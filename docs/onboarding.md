<!--
SPDX-FileCopyrightText: 2025 Thomas Breitner

SPDX-License-Identifier: EUPL-1.2
-->

# Onboarding

RDML provides two access points:

1. a public "front end": {{ '[{base_url}/]({base_url}/)'.format(base_url=base_url) }}
1. a non-public, restricted "back end": {{ '[{base_url}/admin/]({base_url}/admin)'.format(base_url=base_url) }}

To edit data, the following conditions must be met:

1. The editor must be in an authorized IP range.
1. The editor must have the appropriate LDAP/AD group memberships.
1. Depending on the group membership, a distinction can be made between "editors" and "administrators".
1. Users (registered, authorized users) can be assigned to a project or resource as "curators" and in this case are granted editing access to the respective resource.
