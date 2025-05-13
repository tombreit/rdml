<!--
SPDX-FileCopyrightText: 2025 Thomas Breitner

SPDX-License-Identifier: EUPL-1.2
-->

# About

Web based research metadata managment tool & DOI manager & DOI landing pages generator:  
**`rdml`** (**R**esearch**D**ata**M**anagement**L**ight)

## Goals & Features

- (Institutional) Branding (eg. Institut name, logo files) configurable
- **Stakeholders**
    1. Data managers (Backend, authorized)
    1. Data editors (Backend, authorized)
    1. Users (Frontend, anonymus)
- **Manage research projects**
    1. Collect metadata for projects
    1. Assign valid, unique and "speaking" identifiers to projects
    1. Provide web based admin interface for research meta data
    1. Provide stripped down interface for researchers to maintain data for their projects
    1. Provide workflow for research data managers to verify/validate/publish dirty data from researchers
- **Manage research-related metadata**
    - Persons
    - Organizational units
    - Controlled vocabularies
    - ...
- **Provide interface to register and update DOIs and metadata**
    - Builtin web based interface to register and update DOI (via Datacite API)
    - Manage DOIs for projects
        - Register DOI and set metadata for resources without a DOI
        - Update DOI metadata for existing DOI resources
    - Manage DOIs for other "DOI eligible" data (datasets etc.)
    - Logs DataCite operations
- **Provide public landing page for a DOI**
    1. Resolve DOIs to a landing page
    1. Ensure DOIs resolve to a persistent landing page
    1. Landing page must provide some data, some is optional
    1. Resolve DOIs to tombstone landing page if project gets cancelled
- **[upcoming]**
    - Tombstone pages
    - Mobile friendlier public views
    - Citation snippet (Bibtex)
    - Basic reporting facilities (MS Excel or CSV export)
    - Scheduled verification that current DOIs resolve to current project IDs
    - Versioning

## Architecture

- Build with webframework [Django](https://www.djangoproject.com/)
- Database: SQlite or PostgreSQL
- Some [htmx](https://htmx.org/)
- Backend accessible via authorized request and only from valid IP range (when enforced at the webserver level)
