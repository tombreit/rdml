# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2


from .base_models import (
    Resource,
    RelatedResource,
    CreatorPerson,
    ContributorPerson,
    ContributionPosition,
    FileInfo,
)

from .proxy_models import (
    # Project,
    ResearchResource,
)

__all__ = [
    "Resource",
    "RelatedResource",
    "CreatorPerson",
    "ContributorPerson",
    "ContributionPosition",
    "FileInfo",
    "ResearchResource",
]
