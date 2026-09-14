<!--
SPDX-FileCopyrightText: Thomas Breitner

SPDX-License-Identifier: EUPL-1.2
-->

# Administration

For RDML administrators. For users see [Onboarding](onboarding).

## Access layers

Every layer must be passed:

1. **IP range**
    - Restricts: backend, login, dashboard, DOI manager. Not the public frontend.
    - Allowed IP address ranges: {{ ip_ranges_allowed }}
    - Setting: `RDML_EDIT_ALLOWED_IP_RANGES` (`.env`)
1. **LDAP login**
    - Username: institute email (LDAP `mail`)
    - The RDML user is created at the first login.
1. **LDAP groups → user flags**, set at *every* login:
    - `AUTH_LDAP_GROUP_STAFF`: active + staff (may log in to the backend)
    - `AUTH_LDAP_GROUP_SUPERUSERS`: active + staff + superuser
    - In none of these groups: inactive, login fails.
    - Manual changes of these flags in the backend are overwritten at the next login.
1. **Django groups → model permissions**
    - LDAP groups listed in `AUTH_LDAP_MIRROR_GROUPS_LIST` are mirrored as Django groups. Membership is synced at every login.
    - Permissions are assigned to these groups: *Backend › Accounts › Groups*
    - No groups or permissions are created automatically. See [Group permissions](#group-permissions).
1. **Curators** (per research resource)
    - A curator may edit this research resource, even without the *change research resource* permission.
    - Not sufficient alone. See [Curators](#curators).
1. **DOI permission**
    - `doimanager | datacite resource | Can register and update DOI records`
    - The research resource must be public.

## Roles

| Role | LDAP groups | Django group |
|------|-------------|--------------|
| *Curator* | `AUTH_LDAP_GROUP_STAFF` + `rdml-editors` | `rdml-editors` |
| *Administrator* | `AUTH_LDAP_GROUP_STAFF` + `rdml-admins` | `rdml-admins` |
| *Superuser* | `AUTH_LDAP_GROUP_SUPERUSERS` | – |

Group names are examples. They must match the LDAP group names in `AUTH_LDAP_MIRROR_GROUPS_LIST`.

```{note}
*Curators* ≠ *Creators*:

- `Resource.curators`: RDML users. Grants edit permission.
- `Resource.creators`: persons (*Organization › Persons*). DataCite metadata only. No login, no permissions.
```

## Curators

What a curator without further permissions gets:

1. Can open and save their research resources via direct URL.
1. Cannot open other research resources.
1. No research resource listing, i.e. the dashboard link *N yours* fails. Needs `research | research resource | Can view`.
1. No inlines (creators, data files description, related resources). Needs add/change/delete on these models.
1. No autocomplete search (publisher, curators, keywords, …). Needs *view* on the linked model.
1. No *+* (add) buttons next to linked fields. Needs *add* on the linked model.
1. No *Audit*. Needs `auditlog | log entry | Can view`.
1. Cannot add research resources. Needs `research | research resource | Can add`.
1. Cannot delete research resources. Superusers only, regardless of permissions.

These rules are covered by `rdml/research/tests/test_curator_permissions.py`.

## Group permissions

One-time setup per installation: *Backend › Accounts › Groups*

1. `rdml-editors`
    - research | research resource | Can view
    - research | creator | Can add, change, delete, view
    - research | file information | Can add, change, delete, view
    - research | related resource | Can add, change, delete, view
    - research | contribution position | Can view
    - organization | organization, organizational unit | Can view
    - organization | person | Can add, view
    - accounts | user | Can view
    - classification | all models | Can view
    - classification | classification keyword | Can add
    - auditlog | log entry | Can view
1. `rdml-admins`
    - all permissions of `rdml-editors`
    - research | research resource | Can add, change
    - research | contribution position | Can add, change
    - organization | organization, organizational unit, person | Can add, change
    - classification | all models | Can add, change
    - doimanager | datacite resource | Can view, change
    - doimanager | datacite resource | Can register and update DOI records

## Onboard a new person

1. Network: the person must work from an allowed IP range (e.g. via VPN).
1. Ask IT to add the person to the LDAP groups of the role, see [Roles](#roles).
1. Do not set *staff*, *superuser* or *groups* manually in the backend; they are overwritten at the next login.
1. The person logs in once: {{ '[{base_url}/dashboard/]({base_url}/dashboard/)'.format(base_url=base_url) }}
1. Check *Backend › Accounts › Users*:
    - *Active*, *Staff status* checked
    - *Groups*: expected Django group
    - Group missing: LDAP group listed in `AUTH_LDAP_MIRROR_GROUPS_LIST`?
1. If the person is also an author: create or check *Backend › Organization › Persons* (name, email, ORCID, organization).
1. For each research resource: *WORKFLOW › Curators* › add the user.
1. The person checks: dashboard *N yours*, open and save a research resource.

## Offboard a person

1. Ask IT to remove the person from the LDAP groups. The account is deactivated at the next login attempt.
1. Remove the user from *Curators* of their research resources: *Backend › Research resources › filter by curators*.

## Add a research resource

1. Check or create:
    - *Organization* (publisher)
    - *Organizational unit*
    - *Persons* for all creators
1. *Backend › Research resources › Add*
1. Fill in the required fields, add curators, save.
1. Tell the curators. Further steps: [Onboarding](onboarding).
