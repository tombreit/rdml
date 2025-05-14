<!--
SPDX-FileCopyrightText: 2025 Thomas Breitner

SPDX-License-Identifier: EUPL-1.2
-->

# FAQ

`````{dropdown} Where is the admin interface?

Admin/Backend URL: {{ '[{base_url}/dashboard/]({base_url}/dashboard/)'.format(base_url=base_url) }}
`````

`````{dropdown} What credentials can I use to log in?

Provided that the necessary permissions and group memberships have been set:

Admin/Backend URL: {{ '[{base_url}/dashboard/]({base_url}/dashboard/)'.format(base_url=base_url) }}  
Username: *your-institute-email*  
Password: *your-institute-password*
`````

`````{dropdown} Why can't I log in even the provided credentials are correct?

Login or using some parts of RDML are restricted based on the network (IP address) your request originates.

Allowed IP address ranges: {{ ip_ranges_allowed }}
`````
